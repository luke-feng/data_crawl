#coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import tqdm
localFile = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/html/Grant Street Group - Results - Bonds.html'
import random

def get_urls_from_file(localFile):
    titleLink = []
    termLink = []
    localHtml = open(localFile, 'r', encoding='utf-8')
    htmlHandle = localHtml.read()
    htmlHandle = htmlHandle.replace('&amp;', '&')
    htmlHandle = htmlHandle.replace('&nbsp;', ' ')
    soup = BeautifulSoup(htmlHandle, 'lxml')
    trs = soup.select(
        'body>#container>#subpagecontent>#datatable_wrapper>#datatable>tbody>tr')
    tc = 0
    ic = 0
    for tr in trs:
        title = tr.find("td", "title").find('a')
        if title is not None:
            link = title['href']
            titleLink.append(link)
            tc += 1
        else:
            titleLink.append(' ')
        term = tr.find("td", "links").find_all('a')
        for t in term:
            if 'Terms' in t.get_text():
                link = t['href']
                termLink.append(link)
                ic += 1
            else:
                termLink.append(' ')
    print("There are {} links and {} terms in total.".format(tc, ic))
    return titleLink, termLink


def write_links_to_file(path):
    link_file = path+'link.txt'
    with open(link_file, 'w') as out:
        titleLink, termLink = get_urls_from_file(localFile)
        for i in range(0, len(titleLink)):
            out.write('link \t' + titleLink[i]+'\n')
            out.write('term \t' + termLink[i]+'\n')
    out.close()


def get_page(url):
    try:
        webPage = requests.get(url)
    except requests.ConnectionError:
        print("Can't connect to the site, sorry")
    else:
        page = webPage.text
        page = page.replace('</br>', '\n')
        page = page.replace('&amp;', '&')
        page = page.replace('&nbsp;', ' ')
        return page


def get_file_name(url):
    matchObj = re.match(r'(.*?)results/(.*?)/bid_summary', url, re.M | re.I)
    if matchObj:
        return matchObj.group(2)
    else:
        r = random.randint(0,1000000)
        return str(r)
        print('get name error, return a random name {}'.format(r))
        print(url)


def get_text(url):
    page = get_page(url)
    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
        text = soup.get_text(separator='\n', strip=True)
    else:
        text = ''
    return text


def write_text_to_file(path):
    titleLink, termLink = get_urls_from_file(localFile)
    count = len(titleLink)
    par = tqdm.tqdm(total=count)
    for i in range(0, count):
        par.update(1)
        if titleLink[i] is not ' ':
            fm = get_file_name(titleLink[i])
            fileName = path + fm + '_summary.txt'
            with open(fileName, 'w') as sumOut:
                summary = get_text(titleLink[i])
                sumOut.write(summary)
                sumOut.close()
            if termLink[i] is not ' ':
                termName = path + fm + '_terms.txt'
                with open(termName, 'w') as termOut:
                    term = get_text(termLink[i])
                    termOut.write(term)
                    termOut.close()


linkFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/html/'
dataFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/text/'
write_text_to_file(dataFilePath)
