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
from random import randint

# url = 'http://list.didsoft.com/get?email=luke-feng@outlook.com&pass=v3m76u&pid=http3000&showcountry=yes&country=GB'
# resp = requests.get(url)
# json_data = resp.text
# print(json_data)

PROXY = '193.149.225.9:80'
chrome_path = 'C:/Program Files/Google/Chrome/Application/chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument("--log-level=OFF")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--headless')
chrome_options.add_argument('--proxy-server={}'.format(PROXY))
driver = webdriver.Chrome(
    executable_path=chrome_path, options=chrome_options)

driver.get('https://www.google.com')
print(driver.page_source)
driver.close()