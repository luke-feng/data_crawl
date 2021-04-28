# coding: utf-8
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
import requests

# url = 'http://dps.kdlapi.com/api/getdps/?orderid=911955699122279&num=2&pt=1&format=json&sep=1'
# resp = requests.get(url)
# json_data = resp.json()
# proxylist = json_data['data']['proxy_list']
# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--log-level=1')

# for PROXY in proxylist:
#     try:
#         chrome_options.add_argument('--proxy-server={0}'.format(PROXY))
#         chrome_path = 'C:/Program Files/Google/Chrome/Application/chromedriver.exe'
#         driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
#         driver.set_page_load_timeout(5)
#         driver.get('https://www.baidu.com')
#         id = driver.find_element_by_class_name('title-content-title').text
#         print(id)
#         print(PROXY)
#     except Exception as exc:
#         print(exc)
#         continue
    
    






























'''chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(
            executable_path='C:/Program Files/Google/Chrome/Application/chromedriver.exe', options=chrome_options)
url = 'https://www.phocuswire.com/JetBlues-and-El-Als-venture-arms-open-a-travel-startup-accelerator'
driver.get(url)
source = driver.page_source
from gne import GeneralNewsExtractor
html=source
extractor = GeneralNewsExtractor()
result = extractor.extract(html)
print(result)'''


# from newsplease import NewsPlease
'''path = 'D:/git/data_crawl/raw_data/t.csv'
ls = []
with open(path, 'r') as o:
    for line in o:
        ls.append(line)
    o.close()
urls = ['https://www.dailycamera.com/2017/09/18/boulders-the-pros-closet-raises-9m-to-aid-growth/', 'https://www.usine-digitale.fr/article/telecom-sante-leve-8-millions-d-euros-pour-numeriser-les-hopitaux.N564602','http://flashpoint.gatech.edu/fall-2015/']
try:
    results = NewsPlease.from_urls(urls, timeout=0.1)
    for res in results:
        print(results[res].title)
except Exception as exc:
    print('generated an exception: %s' % (exc))'''





'''urls = ['https://www.dailycamera.com/2017/09/18/boulders-the-pros-closet-raises-9m-to-aid-growth/', 'https://www.usine-digitale.fr/article/telecom-sante-leve-8-millions-d-euros-pour-numeriser-les-hopitaux.N564602']
basepath  = 'D:/git/data_crawl/raw_data/'
with open(basepath + 't.json', 'w') as outfile:
    for url in urls:
        article = NewsPlease.from_url(url)
        result = dict()
        result["date_publish"] = str(article.date_publish)
        result["language"] = article.language
        result["source_domain"] = article.source_domain
        result["maintext"] = article.maintext
        result["title_NP"] = article.title
        result["filename"] = article.filename
        json.dump(result,outfile, indent=4, sort_keys=True)
        outfile.write('\n')'''




'''article = NewsPlease.from_url('https://www.dailycamera.com/2017/09/18/boulders-the-pros-closet-raises-9m-to-aid-growth/')

result = dict()
result["date_publish"] = str(article.date_publish)
result["language"] = article.language
result["source_domain"] = article.source_domain
result["maintext"] = article.maintext
result["title_NP"] = article.title
result["filename"] = article.filename
print(result)'''
'''with open(basepath + 't.json', 'w') as outfile:
    json.dump(result,outfile, indent=4, sort_keys=True)
    outfile.close()'''

'''content = driver.find_elements_by_class_name('release-body.container ')
time = driver.find_elements_by_tag_name('time')
#time = driver.find_elements_by_class_name('mb-no')
title = driver.find_elements_by_tag_name('h1')
print(len(content))
if len(content)>0:
    c = content[0].text
    print(c)
print(len(time))
if len(time)>0:
    c = time[0].text
    print(c)
if len(title)>0:
    print(len(title))
    c = title[0].text
    print(len(c))
    print(c)
driver.close()'''

# from newsplease import SimpleCrawler
# import socket
# import copy
# import threading
# import logging
# import datetime
# import requests
# import urllib3


# def fetch_urls(urls, timeout=None):
#     """
#     Crawls the html content of all given urls in parallel. Returns when all requests are processed.
#     :param urls:
#     :param timeout: in seconds, if None, the urllib default is used
#     :return:
#     """
#     threads = [threading.Thread(target=SimpleCrawler._fetch_url, args=(url, True, timeout)) for url in urls]
#     for thread in threads:
#         try:
#             thread.start()
#         except Exception:
#             pass
#     for thread in threads:
#         try:
#             thread.join()
#         except Exception:
#             pass

#     results = copy.deepcopy(SimpleCrawler._results)
#     SimpleCrawler._results = {}
#     return results

# def new_content(url):
#     content = dict()
#     content["url"] = url
#     content["date_publish"] = ''
#     content["language"] = ''
#     content["source_domain"] = ''
#     content["maintext"] = ''
#     content["title_NP"] = ''
#     content["content_length"] = ''
#     return content

# def from_urls(urls, timeout=None):
#     """
#     Crawls articles from the urls and extracts relevant information.
#     :param urls:
#     :param timeout: in seconds, if None, the urllib default is used
#     :return: A dict containing given URLs as keys, and extracted information as corresponding values.
#     """
#     results = {}
#     download_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     if len(urls) == 0:
#         # Nested blocks of code should not be left empty.
#         # When a block contains a comment, this block is not considered to be empty
#         pass
#     elif len(urls) == 1:
#         url = urls[0]
#         html = fetch_url(url, timeout=timeout)
#         results[url] = NewsPlease.from_html(html, url, download_date)
#     else:
#         results = fetch_urls(urls, timeout=timeout)
#         for url in results:
#             try:
#                 results[url] = NewsPlease.from_html(results[url], url, download_date)
#             except Exception:
#                 results[url] = None
#                 pass
#     return results

# path = 'D:/git/data_crawl/raw_data/t.csv'
# ls = []
# with open(path, 'r') as o:
#     for line in o:
#         ls.append(line)
#     o.close()
# urls = ls
# try:
#     results = from_urls(urls, timeout=1)
#     for res in results:
#         print(res)
#         if results[res] != None:
#             print(results[res].title)
# except Exception as exc:
#     print('generated an exception: %s' % (exc))