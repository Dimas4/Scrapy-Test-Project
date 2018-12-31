# -*- coding: utf-8 -*-
import pandas as pd
import scrapy

from scrapy.http import FormRequest, Request

from config.get_config import get_config


class ArccSpider(scrapy.Spider):
    name = 'arcc'
    allowed_domains = ['arcc-acclaim.sdcounty.ca.gov']
    start_urls = ['https://arcc-acclaim.sdcounty.ca.gov/search/SearchTypeRecordDate']

    def __init__(self):
        self.config = get_config()
        self.scrapy_config = self.config['scrapy']
        self.date = self.scrapy_config['date']

    def parse(self, response):
        return [FormRequest.from_response(response, callback=self.after_submit)]

    def after_submit(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'RecordDate': self.date},
            callback=self.after_choosing_date
        )

    def after_choosing_date(self, response):
        yield Request(url='https://arcc-acclaim.sdcounty.ca.gov/Search/ExportCsv', callback=self.parse_csv)

    def parse_csv(self, response):
        with open('file_to_process.csv', 'w') as file:
            file.write(response.body.decode('utf-8'))

        df = pd.read_csv('file_to_process.csv')

        new_df = pd.DataFrame()
        new_df['grantor'] = df['DirectName']
        new_df['grantee'] = df['IndirectName']
        new_df['doc_number'] = df['InstrumentNumber']
        new_df['record_date'] = df['RecordDate']
        new_df['apn'] = df['ParcelNumber']
        new_df['country'] = 'San Diego'
        new_df['state'] = 'CA'
        new_df['doc_type'] = df['DocTypeDescription']

        new_df.to_csv('result.csv')
