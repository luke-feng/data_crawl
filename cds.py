import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import xlwt
import tqdm
import fiscal_advisors as fa


def get_results_page_info(webPage, fileName, dataFilePath):
    """
    get all basic information from the results page, save it to a tsv file; get all the summary pages and save them to local data path
    :param webPage: source code of the results page
    :param fileName: output tsv file name
    :param dataFilePath: output text file path/dir
    :return summaryLinks: List like data type, all summary links 
    """
    summaryLinks = []
    soup = BeautifulSoup(webPage, 'lxml')
    trs = soup.select(
        'body>#container>#subpagecontent>#datatable_wrapper>#datatable>tbody>tr')
    count = len(trs)
    tc = 0
    ic = 0
    with open(fileName, 'w') as out:
        out.write('Id'+'\t'+'Auction_Name'+'\t'+'Date'+'\t'+'Principal'+'\t'+'Issuer'+'\t' +
                  'State'+'\t'+'Site'+'\t'+'Description'+'\t'+'Summary_link'+'\n')
        par = tqdm.tqdm(total=count)
        for tr in trs:
            par.update(1)
            Id = tr['id']
            date = tr.find("td", "date sorting_1").get_text()
            principal = tr.find("td", "principal").get_text()
            state = tr.find("td", "state").get_text()
            site = tr.find("td", "site").get_text()
            description = tr.find("td", "description").get_text()
            title = tr.find("td", "title").find('a')
            issuer = title.get_text()
            summaryLink = title['href']
            summaryLinks.append(summaryLink)
            fileTitle = fa.get_file_name(summaryLink)
            summaryName = dataFilePath + fileTitle + '_summary.txt'
            with open(summaryName, 'w') as sumOut:
                summary = fa.get_text(summaryLink)
                sumOut.write(summary)
                sumOut.close()
            tc += 1
            out.write(Id+'\t'+fileTitle+'\t'+date+'\t'+principal+'\t'+issuer+'\t' +
                      state+'\t'+site+'\t'+description+'\t'+summaryLink+'\n')
        out.close()
    print("There are {} links in total.".format(tc))
    return summaryLinks


def get_summary(fileTitle, dataFilePath, localTextFile):
    """
    turn the summary raw data to a structured data result
    :param fileTitle: page title/name
    :param dataFilePath: the raw txt data path
    :param localTextFile: all local raw text within a list
    :return allValue: dict like data type, the structured reuslts
    """
    allValue = dict()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    allValue['auctionDate'] = ''
    allValue['auctionTypes'] = ''
    allValue['auctionStart'] = ''
    allValue['auctionEnd'] = ''
    allValue['auctionLastUpdate'] = ''
    allValue['auctionStatus'] = ''
    allValue['notice'] = ''
    allValue['principal'] = ''
    allValue['issuer'] = ''
    allValue['description'] = ''
    allValue['inTheMoney'] = ''
    allValue['outOfTheMoney'] = ''

    if fileName in localTextFile:
        text = localTextFile[fileName]
        for line in text:
            currentIndex = text.index(line)
            line = line.strip()
            if line == 'Auction Status':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
                types = text[currentIndex+2]
                allValue['auctionTypes'] = types
                start = text[currentIndex+3]
                allValue['auctionStart'] = start
                end = text[currentIndex+4]
                allValue['auctionEnd'] = end
                lastUpdate = text[currentIndex+5]
                allValue['auctionLastUpdate'] = lastUpdate
                status = text[currentIndex+6]
                allValue['auctionStatus'] = status
                if text[currentIndex+7] == 'NOTICE:':
                    notice = 'NOTICE: '+text[currentIndex+8]
                    allValue['notice'] = notice
                    principal = text[currentIndex+9]
                    allValue['principal'] = principal
                    issuer = text[currentIndex+10]
                    allValue['issuer'] = issuer
                    i = currentIndex + 11
                    description = ''
                    while text[i].startswith('IN-THE-MONEY') is False:
                        description = description+text[i]+'\n'
                        i += 1
                    allValue['description'] = description
                if text[currentIndex+7].startswith('$'):
                    principal = text[currentIndex+7]
                    allValue['principal'] = principal
                    issuer = text[currentIndex+8]
                    allValue['issuer'] = issuer
                    i = currentIndex + 9
                    description = ''
                    while text[i].startswith('IN-THE-MONEY') is False:
                        description = description+text[i]+'\n'
                        i += 1
                    allValue['description'] = description

            elif line == 'IN-THE-MONEY':
                i = currentIndex+1
                j = 0
                form = 'IN-THE-MONEY\n'
                while 'OUT-OF-THE-MONEY' not in text[i]:
                    if j % 6 == 0:
                        form = form+'\n'+text[i]
                        j += 1
                    elif (text[i].startswith('(')) or (text[i].startswith('Amount')):
                        form = form+' '+text[i]
                    else:
                        form = form+'| '+text[i]
                        j += 1
                    i += 1
                allValue['inTheMoney'] = form
            elif line == 'OUT-OF-THE-MONEY':
                i = currentIndex+1
                j = 0
                form = 'OUT-OF-THE-MONEY\n'
                while 'Click below to' not in text[i]:
                    if j % 6 == 0:
                        form = form+'\n'+text[i]
                        j += 1
                    elif (text[i].startswith('(')) or (text[i].startswith('Amount')):
                        form = form+' '+text[i]
                    else:
                        form = form+'| '+text[i]
                        j += 1
                    i += 1
                allValue['outOfTheMoney'] = form
    return allValue


def writeFianlResults(resultPageFile, dataFilePath, outputFile):
    """
    write all results to a xls file
    :param resultPageFile: the tsv file of the first page information
    :param dataFilePath: raw text file path/dir
    :param outputFile: output xls file name
    """
    localTextFile = fa.get_all_local_text(dataFilePath)
    xlsFile = xlwt.Workbook()
    sheet1 = xlsFile.add_sheet('results', cell_overwrite_ok=True)

    header = ['Id', 'Auction Name', 'Date', 'Principal', 'Issuer', 'State', 'Site', 'Description', 'Summary link',
              'Auction Date', 'Auction Types', 'Auction Start', 'Auction End', 'Auction Last Update', 'Auction Status',
              'Auction Notice', 'Auction Principal', 'Auction Issuer', 'Auction Description',  'IN-THE-MONEY', 'OUT-OF-THE-MONEY']

    for i in range(0, len(header)):
        sheet1.write(0, i, header[i])

    with open(resultPageFile, 'r') as rp:
        i = 1
        par = tqdm.tqdm()
        for line in rp:
            par.update(1)
            tokens = line.split('\t')
            fileTitle = tokens[1]
            allValue = get_summary(
                fileTitle, dataFilePath, localTextFile)
            if tokens[0].startswith('Id') is False:
                for col in range(0, len(tokens)):
                    sheet1.write(i, col, tokens[col])
                col = len(tokens)
                for v in allValue:
                    sheet1.write(i, col, allValue[v])
                    col += 1
                i += 1
    xlsFile.save(outputFile)

def main():
    '''
    main function
    '''
    # the local file path for the results(.tsv and .xls), you need to change it to your local path, like: '/Users/user/Documents/raw_data/linkfilepath/'
    linkFilePath = you need to change'
    # the local file path for the all rew data(.txt), you need to change it to your local path, like: '/Users/user/Documents/raw_data/datafilepath/'
    dataFilePath = 'you need to change'
    # file path and name of the fianl results
    outputFile = linkFilePath + 'final_cds.xls'
    # output file path and name for the tsv file of search results webpage
    resultPageFile = linkFilePath+'results_page_info.tsv'
    # url of search results webpage
    url = 'https://auctions.grantstreet.com/results/cd'
    webPage = fa.get_all_trs(url)
    get_results_page_info(webPage, resultPageFile, dataFilePath)
    writeFianlResults(resultPageFile, dataFilePath, outputFile)


if __name__ == "__main__":
    main()
