# -*- coding: utf-8 -*-
import time

import scrapy

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
        self.driver.get(self.start_urls[0])
        self.find_and_click('#btnButton')

        time.sleep(1)

        for date in self.scrapy_config['dates']:
            input = self.driver.find_element_by_css_selector('#RecordDate')
            input.clear()
            input.send_keys(date)

            self.find_and_click('#btnSearch')

            time.sleep(10)

            page_count = self.get_page_count()

            if self.scrapy_config['page_count'] != 'all':
                page_count = self.scrapy_config['page_count']

            for _ in range(page_count):
                time.sleep(10)

                trs = self.driver.find_element_by_xpath('//*[@id="RsltsGrid"]/div[4]/table/tbody')\
                    .find_elements_by_css_selector('tr')

                row_count = len(trs)

                if self.scrapy_config['row_count'] != 'all':
                    row_count = self.scrapy_config['row_count']

                for tr in trs[:row_count]:
                    time.sleep(3)

                    try:
                        tr.click()
                    except Exception as err:
                        time.sleep(5)
                        tr.click()

                    main_window_handle = self.driver.current_window_handle

                    apn = tr.find_elements_by_tag_name('td')[8].text
                    print(apn)

                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(7)

                    results = self.driver.find_elements_by_css_selector('.docDetailRow')

                    while True:
                        results = self.driver.find_elements_by_css_selector('.docDetailRow')
                        if len(results) < 5:
                            time.sleep(5)
                        else:
                            break

                    record_date = results[0].find_element_by_class_name('formInput').text

                    document = results[3].find_element_by_class_name('formInput').text
                    doc_type = results[6].find_element_by_class_name('listDocDetails').text
                    grantors = results[7].find_element_by_class_name('listDocDetails').find_elements_by_tag_name('span')
                    grantees = results[8].find_element_by_class_name('listDocDetails').find_elements_by_tag_name('span')

                    grantor_result = [grantor.text for grantor in grantors]
                    grantee_result = [grantee.text for grantee in grantees]

                    data = {
                        'record_date': record_date,
                        'doc_number': document,
                        'doc_type': doc_type,
                        'name': grantee_result,
                        'role': grantor_result or grantee_result,
                        'apn': apn,
                        'county': 'San Diego',
                        'state': 'CA',
                    }

                    self.driver.close()
                    self.driver.switch_to.window(main_window_handle)

                    print(data)

                    yield data

                next = self.driver.find_elements_by_css_selector('span.t-icon.t-arrow-next')[0]
                next.click()

        self.driver.close()
