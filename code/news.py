# coding: utf-8
from newsplease import NewsPlease
import os
import io
import sys
import json
import pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
source_path = 'D:/git/data_crawl/raw_data/'
newslink_path = 'D:/git/data_crawl/raw_data/newslink.csv'

xl = pd.read_csv(newslink_path, index_col=None, header=None)
urls = xl[0].values.tolist()
resultPath = source_path + 'news.json'
with open(resultPath, 'w') as outfile:
    try:
        results = NewsPlease.from_urls(urls, timeout=1)
        for article in results:
            content = dict()
            content["date_publish"] = str(result[article].date_publish)
            content["language"] = result[article].language
            content["source_domain"] = result[article].source_domain
            content["maintext"] = result[article].maintext
            content["title_NP"] = result[article].title
            content["content_length"] = get_content_length(content["maintext"])
            json.dump(content, outfile, indent=4, sort_keys=True)
    except Exception as exc:
        print('generated an exception: %s' % (exc))

def get_content_length(content):
        content_length = 0
        clist = content.split()
        content_length = len(clist)
        return content_length