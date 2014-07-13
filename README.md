# Slovak Company Register

This script is scraping data from Slovak Business Registry (ORSR: http://www.orsr.sk/).

## Status

Current motivation for maintaining this script is:

* keep it going even after ScraperWiki Classic goes down
* maybe enhance it so that it may complement [Organizations dataset from Datanest](http://datanest.fair-play.sk/datasets/1)
  * i.e. list also board members, owners, etc.

## TODO

* maxn is quite arbitrary set manually to 100000 - we need a better way to determine we are at the end, especially for say SID-6, where say 305633 is valid ID
* it seems like HTTP response code 500 is no longer used by ORSR => investigate and update the code

## History

Scraper was migrated from ScraperWiki Classic (as they are slowly turning the service off):

https://classic.scraperwiki.com/scrapers/sk_company_numbers/


to Morph.io (who for now seems a good successor for ScraperWiki):

https://morph.io/hanecak/scraper-sk_company_register
