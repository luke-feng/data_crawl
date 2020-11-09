import requests
from bs4 import BeautifulSoup
import re

localFile = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/CDs/html/Grant Street Group - Results - CDs.html'


def get_urls_from_file(localFile):
    titleLink = []
    localHtml = open(localFile, 'r', encoding='utf-8')
    htmlHandle = localHtml.read()
    htmlHandle = htmlHandle.replace('&amp;', '&')
    htmlHandle = htmlHandle.replace('&nbsp;', ' ')
    soup = BeautifulSoup(htmlHandle, 'lxml')
    trs = soup.select(
        'body>#container>#subpagecontent>#datatable_wrapper>#datatable>tbody>tr')
    tc = 0
    for tr in trs:
        title = tr.find("td", "title").find('a')
        if title is not None:
            link = title['href']
            titleLink.append(link)
            tc += 1
        else:
            titleLink.append(' ')
    print("There are {} links".format(tc))
    return titleLink

def write_links_to_file(path):
    link_file = path+'link.txt'
    with open(link_file, 'w') as out:
        titleLink = get_urls_from_file(localFile)
        for i in range(0, len(titleLink)):
            out.write('link \t' + titleLink[i]+'\n')
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
        print('get name error')


def get_text(url):
    page = get_page(url)
    soup = BeautifulSoup(page, 'lxml')
    text = soup.get_text(separator='\n', strip=True)
    return text


def write_text_to_file(path):
    titleLink = get_urls_from_file(localFile)
    for i in range(0, len(titleLink)):
        if titleLink[i] is not ' ':
            fm = get_file_name(titleLink[i])
            fileName = path + fm + '_summary.txt'
            with open(fileName, 'w') as sumOut:
                summary = get_text(titleLink[i])
                sumOut.write(summary)
                sumOut.close()
            

linkFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/CDs/html/'
write_links_to_file(linkFilePath)
dataFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/CDs/text/'
write_text_to_file(dataFilePath)