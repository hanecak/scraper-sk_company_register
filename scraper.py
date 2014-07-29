#!/usr/bin/python
# -*- coding: utf-8 -*-
import scraperwiki                                                                    
import urllib2
from time import sleep
from string import join
import re

def strips(s):
    "strip('<p>foo bar&nbsp;</p>' => foo bar baz"
    e = re.compile(r'<.*?>')
    ee = re.compile(r'\s+|&nbsp;')
    return ee.sub(' ', e.sub('', s))

def extract(t, s):
    """s = ['Identification number wfefwe: 31 382 266', 'Business name: foo bar baz', ...]
    extract('Identification number', s) => 31 382 266"""
    s = filter(lambda x: t in x, s)
    if s:
        return re.split(':', s[0])[-1]
    else:
        return 'n/a'

def parse_html(html):
    s = re.split(r' \(from: .*?\)', strips(html))
    # It seems that at some point in the past, ORSR was sending HTTP response
    # 500 for non-existent IDs. But now it does not. Instead, it sends page with
    # just header and footer.
    if len(s) <= 1:
        # skip non-existent ID
        return False
    
    cname = extract('Business name:', s)
    if cname == 'n/a':
        extract('Business name of the organisational unit:', s)
    if len(cname) > 3:
        caddress = extract('Registered seat:', s)
        if caddress == 'n/a':
            caddress = extract('Place of business', s)
        cnumber = extract(r'Identification number', s)
        cfounding = extract('Date of entry', s)
        ctype = extract('Legal form:', s)
        ccapital = extract('Registered capital:', s)
        if ccapital == 'n/a':
            ccapital = extract('Capital:', s)
        if filter(lambda x: 'Date of deletion' in x, s) or filter(lambda x: 'Liquidators:' in x, s):
            cstatus = 'DISSOLVED'
        else:
            cstatus = 'LIVE'
        persons = ''
        if ctype != 'Self-employed individual':
            ss = join(s, sep=" ")
            persons = ss[ss.find('Management body:')+17:ss.find('Acting:')]
        else:
            persons = re.sub('-.*','', cname)
        if 'JUSTICE' in persons:
            persons = 'n/a'
        cpersons = persons.strip(' ;').replace('    ', '; ')
        return [cname, caddress, cnumber, cfounding, ctype, ccapital, cstatus, cpersons]
    else:
        return False

# court list: Look at the source code of
# http://www.orsr.sk/search_subjekt.asp?lan=en and search for "SID":
court_list = [
              # SID, court name
              [2, 'District Court Bratislava I'],
              [3, 'District Court Banská Bystrica'],
              [4, 'District Court Košice I'],
              [5, 'District Court Nitra'],
              [6, 'District Court Prešov'],
              [7, 'District Court Trenčín'],
              [8, 'District Court Trnava'],
              [9, 'District Court Žilina']
              ]

# TODO: As of now, this is an arbitrary limit. There will come time when there
# will be more companies than that. Thus, it would be nice to determined "the
# end" in some reliable and automatic fashion.
maxn = 400000
# To skip scanning few hundred thousands of empty pages uselessly, we stop
# scraping pages for a particular court after certain amount of successive IDs d
# not exist. Values observed on small test data were around 40, so hopefully 250
# is good value.
max_id_hole = 250

def go():
    current_id_hole = 0
    n = scraperwiki.sqlite.get_var('id')
    court = scraperwiki.sqlite.get_var('court')
    runs = scraperwiki.sqlite.get_var('runs')
    if n is None:
        n = 0
    if court is None:
        court = 0
    if runs is None:
        runs = 0
    print '### starting work with n = %s and court = %d, runs so far: %s' % (n, court, runs)
    
    while court < len(court_list):
        url_template = 'http://www.orsr.sk/vypis.asp?lan=en&ID=%s&SID=' + str(court_list[court][0]) + '&P=0'
        urls = [ url_template % m for m in range(1, maxn + 1) ]

        for url in urls[n:]:
            retry = 3
            n += 1
            l = None
            while retry:
                print '### URL (retry:', retry, ') No. ', str(n), url
                try:
                    r = urllib2.urlopen(url)
                    l = parse_html(r.read())
                    break
                except Exception as e:
                    print '!!!/\/\/\!!! ERROR %s !!!/\/\/\!!!' % e
                    try:
                        code = e.code
                    except:
                        code = 0
                    if code == 500:
                        retry = 0 # 500 means bad ID, so don't even retry
                    else:
                        retry -= 1
                        sleep(3)
                    print 'Retrying.....'

            # we want to sleep before fetching another url, because of timeouts
            sleep(0.1)

            if not l:
                current_id_hole += 1
                if current_id_hole >= max_id_hole:
                    print 'Ending work for court SID=%d after encountering %d non-existent IDs' % (court_list[court][0], current_id_hole)
                    break
                continue

            current_id_hole = 0

            row = map(lambda x: x.decode('windows-1250'), l)

            # As IDs are duplicated between courts (i.e. ID=1 with
            # SID=2 is different company than ID=1 for SID=3), we
            # need to construct unique ID from both ID and SID:
            company_id = (court_list[court][0] << 32) | n
            row.insert(0, company_id)

            row.append(url)
            row.append(court_list[court][0])
            #for x in row:
            #    print "-->", x

            # sanity check: We are not sure whether same ID is
            # reused by courts (i.e. whether same ID but different
            # SID means two different companies) => so, here we
            # check for duplicates.
            if court != 0:
                # for court = 0 this might be the first run, thus
                # 'swdata' may not exist yet thus query may fail
                stored_court = scraperwiki.sqlite.select("CourtSID FROM swdata WHERE UniqueID = %s" % row[0])
                if len(stored_court) > 0 and stored_court[0]['CourtSID'] != row[10]:
                    print "*** duplicate ID detected: 0x%08X" % row[0]
                    print "*** stored court: '%s', court: '%s'" % (stored_court[0]['CourtSID'], row[10])
                    return

            scraperwiki.sqlite.save(['UniqueID'],
                                {'UniqueID': row[0],
                                 'CompanyName': row[1].strip(),
                                 'CompanyAddress': row[2].strip(),
                                 'CompanyNumber': row[3].strip(),
                                 'CompanyFounding': row[4].strip(),
                                 'EntityType': row[5].strip(),
                                 'CompanyCapital': row[6].strip(),
                                 'Status': row[7],
                                 'CompanyManagers': row[8],
                                 'RegistryUrl': row[9],
                                 'CourtSID': row[10]
                                 })
            scraperwiki.sqlite.save_var('id', n)

        print "All URLs for \"%s\" iterated ..." % court_list[court][1]
        n = 0
        scraperwiki.sqlite.save_var('id', n)
        court += 1
        scraperwiki.sqlite.save_var('court', court)
    
    print "All courts iterated ..."
    court = 0
    scraperwiki.sqlite.save_var('court', court)

    runs += 1
    scraperwiki.sqlite.save_var('runs', runs)


go()
print "All seems to be done"
