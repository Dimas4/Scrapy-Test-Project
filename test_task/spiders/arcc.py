# -*- coding: utf-8 -*-
import time

from selenium import webdriver
import scrapy

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
        self.driver.get('https://arcc-acclaim.sdcounty.ca.gov/search/SearchTypeRecordDate')
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

            for i in range(page_count):
                time.sleep(10)

                trs = self.driver.find_element_by_xpath('//*[@id="RsltsGrid"]/div[4]/table/tbody')\
                    .find_elements_by_css_selector('tr')

                for tr in trs[:self.scrapy_config['row_count']]:
                    time.sleep(2)

                    try:
                        tr.click()
                    except Exception:
                        time.sleep(5)
                        tr.click()

                    main_window_handle = self.driver.current_window_handle

                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    time.sleep(5)

                    results = self.driver.find_elements_by_css_selector('.docDetailRow')

                    grantor_result = []
                    grantee_result = []

                    flag = False

                    while not flag:
                        results = self.driver.find_elements_by_css_selector('.docDetailRow')
                        if len(results) < 5:
                            time.sleep(5)
                        else:
                            flag = True

                    record_date = results[0].find_element_by_class_name('formInput').text

                    document = results[3].find_element_by_class_name('formInput').text
                    doc_type = results[6].find_element_by_class_name('listDocDetails').text
                    grantors = results[7].find_element_by_class_name('listDocDetails').find_elements_by_tag_name('span')
                    grantees = results[8].find_element_by_class_name('listDocDetails').find_elements_by_tag_name('span')

                    for grantor in grantors:
                        grantor_result.append(grantor.text)

                    for grantee in grantees:
                        grantee_result.append(grantee.text)

                    data = {
                        'record_date': record_date,
                        'doc_number': document,
                        'doc_type': doc_type,
                        'name': grantee_result,
                        'role': grantor_result or grantee_result,
                        'county': 'San Diego',
                        'state': 'CA',
                    }

                    self.driver.close()
                    self.driver.switch_to.window(main_window_handle)

                    print(date)

                    yield data

                next = self.driver.find_elements_by_css_selector('span.t-icon.t-arrow-next')[0]
                next.click()

        self.driver.close()
