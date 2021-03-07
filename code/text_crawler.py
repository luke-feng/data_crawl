# coding: utf-8

from newsplease import NewsPlease
import json
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import tqdm
import random
import sys
import os
import io
import sys
import urllib.request
import openpyxl
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
sc_dict = dict()


class newsCrawler:
    def __init__(self):
        self.source_path = 'D:/git/data_crawl/raw_data/'
        self.newslink_file = 'newslink.xlsx'
        self.newslink_path = self.source_path + self.newslink_file
        self.resultPath = self.source_path + 'news.json'
        chrome_options = Options()
        chrome_options.add_argument('--headless')

        self.executor = ThreadPoolExecutor(max_workers=10)
        # for workers
        self.driver1 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver2 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver3 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver4 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver5 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver6 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver7 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver8 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver9 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.driver10 = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
        self.workers = [self.driver1, self.driver2,
                        self.driver3, self.driver4, self.driver5, self.driver6, self.driver7,
                        self.driver8, self.driver9, self.driver10]

    def get_sorce_link(self):
        xl = pd.read_excel(self.newslink_path, index_col=None, header=None)
        return xl

    #

    def get_status_code(self, url):
        try:
            status_code = requests.get(url).status_code
            return status_code
        except Exception as e:
            return 404

    def __del__(self):
        self.driver1.close()
        self.driver2.close()
        self.driver3.close()
        self.driver4.close()
        self.driver5.close()
        self.driver6.close()
        self.driver7.close()
        self.driver8.close()
        self.driver9.close()
        self.driver10.close()
        print('>>>>[Well Done]')

    # def get_title(browser):
    '''par = tqdm.tqdm(ncols=100, total=len(links))
    for link in links[0]:
        par.update(1)
        status_code = get_status_code(link)
        if status_code not in sc_dict:
            sc_dict[status_code] = 1
        else:
            sc_dict[status_code] += 1'''

    def get_information(self, browser, url):
        title = ''
        time = ''
        content = ''
        status_code = ''
        content_length = 0
        result = dict()
        result['url'] = url
        result['status_code'] = self.get_status_code(url)
        result['title'] = ''
        result["date_publish"] = ''
        result["language"] = ''
        result["source_domain"] = ''
        result["maintext"] = ''
        result["title_NP"] = ''
        result["content_length"] = ''

        if result['status_code'] == 200:
            if 'www.sec.gov' not in url:
                browser.get(url)
                title = self.get_title(browser)
                content = self.get_content(url)
        result['url'] = url
        result['title'] = title
        result["date_publish"] = content["date_publish"]
        result["language"] = content["language"]
        result["source_domain"] = content["source_domain"]
        result["maintext"] = content["maintext"]
        result["title_NP"] = content["title_NP"]
        result["content_length"] = get_content_length(content["maintext"])
        return result

    def get_content(self, url):
        article = NewsPlease.from_url(url)
        result = dict()
        result["date_publish"] = str(article.date_publish)
        result["language"] = article.language
        result["source_domain"] = article.source_domain
        result["maintext"] = article.maintext
        result["title_NP"] = article.title
        return result

    def get_title(self, browser):
        title = ''
        hones = browser.find_elements_by_tag_name('h1')
        if len(hones) > 0:
            for h in hones:
                title = hones[0].text
                if len(title) > 0:
                    break
        return title

    def get_content_length(self, content):
        content_length = 0
        clist = content.split()
        content_length = len(clist)
        return content_length

    def asyn_page(self, url_list, results):
        future_to_url = dict()
        for i, url in enumerate(url_list):
            t = self.executor.submit(self.get_information,
                                     browser=self.workers[i], url=url_list[i])
            future_to_url[t] = url
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    def run(self):
        links = self.get_sorce_link()
        urls = links[0].values.tolist()
        par = tqdm.tqdm(ncols=100, total=len(urls))
        with open(self.resultPath, 'w') as outfile:
            start = []
            end = []
            for i in range(0, len(urls), 10):
                start.append(i)
                if i + 10 >= len(urls):
                    end.append(len(urls))
                else:
                    end.append(i+10)
            for i, s in enumerate(start):
                results = []
                self.asyn_page(
                    url_list=urls[start[i]: end[i]], results = results)
                for result in results:
                    json.dump(result, outfile, indent=4, sort_keys=True)
                    outfile.write('\n')
                par.update(10)
            outfile.close()
        print('get webpage finish!')


if __name__ == '__main__':
    newsc = newsCrawler()
    newsc.run()
