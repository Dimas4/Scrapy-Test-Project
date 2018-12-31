# -*- coding: utf-8 -*-
import time

import scrapy

from scrapy.http import FormRequest, Request
from selenium import webdriver

from config.get_config import get_config


class ArccSpider(scrapy.Spider):
    name = 'arcc'
    allowed_domains = ['arcc-acclaim.sdcounty.ca.gov']
    start_urls = ['https://arcc-acclaim.sdcounty.ca.gov/search/SearchTypeRecordDate']

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.config = get_config()
        self.scrapy_config = self.config['scrapy']

    def find_and_click(self, selector):
        object = self.driver.find_element_by_css_selector(selector)
        object.click()

    def get_page_count(self):
        input_page_count = self.driver.find_element_by_css_selector('div.t-page-i-of-n')
        return int(input_page_count.find_element_by_tag_name('input').get_attribute("value"))

    def parse(self, response):
        return [FormRequest.from_response(response,
                                          callback=self.after_submit)]

    def after_submit(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'RecordDate': '11/27/2018'},
            callback=self.after_choosing_date
        )

    def after_choosing_date(self, response):
        yield Request(url='https://arcc-acclaim.sdcounty.ca.gov/Search/ExportCsv', callback=self.parse_csv)

    def parse_csv(self):
        time.sleep(10)

