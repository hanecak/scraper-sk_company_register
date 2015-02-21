# Slovak Company Register

This script is scraping data from Slovak Business Registry (ORSR: http://www.orsr.sk/).

## Data

Data uses English language as employed by ORSR and should be quite straightforward to understand with the only exception of CourtSID.

### CourtSID

* 2: District Court Bratislava I
* 3: District Court Banská Bystrica
* 4: District Court Košice I
* 5: District Court Nitra
* 6: District Court Prešov
* 7: District Court Trenčín
* 8: District Court Trnava
* 9: District Court Žilina

## Status

Current motivation for maintaining this script is:

* keep it going even after ScraperWiki Classic goes down
* maybe enhance it so that it may complement [Organizations dataset from Datanest](http://datanest.fair-play.sk/datasets/1)
  * i.e. list also board members, owners, etc.

## TODO

* separate people into dedicated table (issue #1)

## History

Scraper was migrated from ScraperWiki Classic (as they are slowly turning the service off):

https://classic.scraperwiki.com/scrapers/sk_company_numbers/


to Morph.io (who for now seems a good successor for ScraperWiki):

https://morph.io/soit-sk/scraper-sk_company_register
