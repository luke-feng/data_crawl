# coding: utf-8

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
import xlwt
import io
import sys
import urllib.request
import openpyxl
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from random import randint

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
id_path = 'D:/git/data_crawl/raw_data/Trademark_ID_List.xlsx'


def read_all_ids(id_path):
    '''
    read all ids from excel file
    :param id_path: file path of this excel file
    :return ids: List data type, all ids
    '''
    ids = []
    xl = pd.read_excel(id_path, index_col=None, header=None)
    ids = xl[0].values.tolist()
    return ids


def generate_resultsUrlList(ids):
    '''
    generate result url list
    :param ids: List data type, all ids
    :return resultsUrlList: List data type, all reuslts url
    '''
    resultsUrlList = ['https://trademarks.ipo.gov.uk/ipo-tmcase/page/Results/1/'+id for id in ids]
    historyUrlList = ['https://trademarks.ipo.gov.uk/ipo-tmcase/page/History/1/'+id for id in ids]
    return resultsUrlList

def generate_historyUrlList(ids):
    '''
    generate result url list
    :param ids: List data type, all ids
    :return historyUrlList: List data type, all reuslts url
    '''
    historyUrlList = ['https://trademarks.ipo.gov.uk/ipo-tmcase/page/History/1/'+id for id in ids]
    return historyUrlList

def get_tabs(url):
    sleeptime = randint(2,10)
    time.sleep(sleeptime)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    # PROXY = "61.133.87.228:55443"
    # chrome_options.add_argument('--proxy-server={0}'.format(PROXY))
    chrome_path = 'C:/Program Files/Google/Chrome/Application/chromedriver.exe'
    driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
    tabContents = []
    driver.get(url)    
    print('1' + driver.current_url)
    tabs = driver.find_elements_by_class_name('ui-tabs-panel.ui-corner-bottom.ui-widget-content')
    print(len(tabs))
    for i in range(0, 4):
        if i + 1 <= len(tabs):
            content = tabs[i].text
            tabContents.append(content)
        else:
            content = ''
            tabContents.append(content)
    hist = driver.find_element_by_xpath('/html/body/main/div[4]/div/p[1]/a').click()
    print('3' + hist)
    time.sleep(3)
    print('2' + driver.current_url)
    driver.get(driver.current_url)
    tabs = driver.find_elements_by_class_name('ui-tabs-panel.ui-corner-bottom.ui-widget-content')
    # driver.refresh()
    for i in range(0, 4):
        if i + 1 <= len(tabs):
            content = tabs[i].text
            tabContents.append(content)
        else:
            content = ''
            tabContents.append(content)
    driver.delete_all_cookies()
    driver.quit()
    driver.close()
    return tabContents


def get_results():
    results = dict()
    ids = read_all_ids(id_path)
    resultsUrlList = generate_resultsUrlList(ids)
    historyUrlList = generate_historyUrlList(ids) 
    urls = historyUrlList
    # url = urls[0]
    
    for i in range(0, 1):
        resultsUrl = resultsUrlList[i]
        # historyUrl = historyUrlList[i]
        urlId = ids[i]
        resultsTabContents = get_tabs(resultsUrl)
        # historyTabContents = get_tabs(historyUrl)
        results[urlId] = [urlId] + resultsTabContents
    return results

def write_results(results):
    outputFile = 'D:/git/data_crawl/raw_data/final_Trademark.xlsx'
    xlsFile = openpyxl.Workbook()
    sheet1 = xlsFile.create_sheet(index=0)
    header = ['ID', 'tab-1', 'tab-2', 'tab-3',
                'tab-4', 'tab-1', 'tab-2', 'tab-3', 'tab-4']
    for i in range(1, len(header)+1):
        sheet1.cell(1, i).value = header[i-1]

    i = 2
    for urlId in results:
        for j in range(1, len(header)+1):
            sheet1.cell(i, j).value = header[i-1]
        i+=1
    xlsFile.save(outputFile)


def run():
    results = get_results()
    write_results(results)

if __name__ == "__main__":
    run()


















# for url in urls:
#     sleeptime = randint(10,100)
#     time.sleep(sleeptime)
#     driver.get(url)    
#     Wait(driver, 60).until(
#         Expect.presence_of_element_located(
#             (By.CSS_SELECTOR, 'body>main'))
#     )

#     tabs = driver.find_elements_by_class_name('ui-tabs-panel.ui-corner-bottom.ui-widget-content')
    
#     print(len(tabs))

