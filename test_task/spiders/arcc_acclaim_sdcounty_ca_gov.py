# -*- coding: utf-8 -*-
import scrapy


class ArccAcclaimSdcountyCaGovSpider(scrapy.Spider):
    name = 'arcc-acclaim.sdcounty.ca.gov'
    allowed_domains = ['www.arcc-acclaim.sdcounty.ca.gov/search/SearchTypeRecordDate']
    start_urls = ['http://www.arcc-acclaim.sdcounty.ca.gov/search/SearchTypeRecordDate/']

    def parse(self, response):
        pass
