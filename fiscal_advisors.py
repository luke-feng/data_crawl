# coding: utf-8

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import tqdm
import random
import sys
import os
import xlwt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.chrome.options import Options


def get_all_trs(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)
    input = browser.find_element_by_css_selector(
        'body>#container>#subpagecontent>#datatable_wrapper>.dataTables_header>.dataTables_length>label>select')
    s1 = Select(input)
    s1.select_by_value('-1')
    Wait(browser, 600).until(
        Expect.presence_of_element_located(
            (By.CSS_SELECTOR, "body>#container>#subpagecontent>#datatable_wrapper>#datatable>tbody>tr"))
    )
    page = browser.page_source
    page = page.replace('&amp;', '&')
    page = page.replace('&nbsp;', ' ')
    browser.close()
    print('get webpage finish!')
    return page


def get_page(url):
    if 'www' in url or 'http' in url:
        try:
            webPage = requests.get(url)
        except requests.ConnectionError:
            print("Can't connect to the site {}, sorry".format(url))
        else:
            page = webPage.text
            page = page.replace('</br>', '\n')
            page = page.replace('&amp;', '&')
            page = page.replace('&nbsp;', ' ')
            return page
    else:
        return None


def get_file_name(url):
    matchObj = re.match(r'(.*?)results/(.*?)/', url, re.M | re.I)
    if matchObj:
        return matchObj.group(2)
    else:
        r = random.randint(0, 1000000)
        return str(r)


def get_text(url):
    page = get_page(url)
    if page is not None:
        soup = BeautifulSoup(page, 'lxml')
        text = soup.get_text(separator='\n', strip=True)
    else:
        text = ''
    return text


def get_results_page_info(webPage, fileName, dataFilePath):
    '''localHtml = open(link, 'r', encoding='utf-8')
    htmlHandle = localHtml.read()
    htmlHandle = htmlHandle.replace('&amp;', '&')
    htmlHandle = htmlHandle.replace('&nbsp;', ' ')'''
    summaryLinks = []
    termLinks = []
    soup = BeautifulSoup(webPage, 'lxml')
    trs = soup.select(
        'body>#container>#subpagecontent>#datatable_wrapper>#datatable>tbody>tr')
    count = len(trs)
    tc = 0
    ic = 0
    with open(fileName, 'w') as out:
        out.write('Id'+'\t'+'Auction_Name'+'\t'+'Date'+'\t'+'Principal'+'\t'+'Issuer'+'\t' +
                  'State'+'\t'+'Site'+'\t'+'Description'+'\t'+'Summary_link'+'\t'+'Term_link'+'\n')
        par = tqdm.tqdm(total=count)
        for tr in trs:
            par.update(1)
            Id = tr['id']
            date = tr.find("td", "date sorting_1").get_text()
            principal = tr.find("td", "principal").get_text()
            state = tr.find("td", "state").get_text()
            site = tr.find("td", "site").get_text()
            description = tr.find("td", "description").get_text().replace('\n',' ').replace('\t',' ')
            title = tr.find("td", "title").find('a')
            issuer = title.get_text()
            summaryLink = title['href']
            summaryLinks.append(summaryLink)
            fileTitle = get_file_name(summaryLink)
            summaryName = dataFilePath + fileTitle + '_summary.txt'
            with open(summaryName, 'w') as sumOut:
                summary = get_text(summaryLink)
                sumOut.write(summary)
                sumOut.close()
            tc += 1
            term = tr.find("td", "links").find_all('a')
            termLink = ' '
            for t in term:
                if 'Terms' in t.get_text():
                    termLink = t['href']
                    ic += 1
                    termName = dataFilePath + fileTitle + '_terms.txt'
                    with open(termName, 'w') as termOut:
                        term = get_text(termLink)
                        termOut.write(term)
                        termOut.close()
                    break
                else:
                    termLink = ' '
            termLinks.append(termLink)
            out.write(Id+'\t'+fileTitle+'\t'+date+'\t'+principal+'\t'+issuer+'\t' +
                      state+'\t'+site+'\t'+description+'\t'+summaryLink+'\t'+termLink+'\n')
        out.close()
    print("There are {} links and {} terms in total.".format(tc, ic))
    return summaryLinks, termLinks


def get_encode_pattern(site, fileTitle, dataFilePath, localTextFile):
    pattern1 = ['AICauction', 'BairdAuction', 'BidEhlers', 'BidMass', 'BidUmbaugh',
                'ColumbiaCapitalAuction', 'DavidsonBondAuction',
                'FirstSWauction', 'MuniAuction', 'NSIauction',
                'PDXauction', 'PFMauction', 'PGCorbinAuction',  'ShattuckHammondAuction', 'SpeerAuction']
    pattern2 = ['KNNauction']
    pattern3 = ['DainRauscherAuction']
    pattern4 = ['PGHauction']
    pattern5 = ['FiscalAdvisorsAuction']
    pattern7 = ['UnivSystemOfMaryland.RevBonds.1999B.AON', 'AvonGroveSD.GOs.Series1999.AON', 'MiltonAreaSD.Series1999.AON',
                'HillsboroughCounty.Series1999.AON', 'NorthernYorkSD.Series1999.AON', 'LancasterSD.Series1999.AON',
                'LigonierValleySD.SeriesB1999.MBM', 'LigonierValleySD.SeriesA1999.AON', 'FranklinRegionalSD.Series1999.AON',
                'CrawfordCounty.GOs.Series1999.AON', 'CheltenhamSD.Series1999.AON', 'Monroeville.GOs.1999.AON',
                'DouglasCnty.NV.GOs.Series1999.AON', 'Portland.GOs.Series1999A.AON', 'KingCounty.Series1999.AON', 'GlenviewParkDistrict.Series1999.AON',
                'WashingtonState.GOBonds.Series1999S3.AON', 'WashingtonState.GOs.1999S2.AON', 'Michigan.StateBldgAuth.1999IRevBonds.AON',
                'NYCTFA.1999C.Taxable.AON', 'Portland.LtdTaxRevBonds.1999A.AON', 'NewYorkCity.GOs.Fiscal1999I.AON',
                'SanFrancisco.TaxAllocRevRefBonds.1999B.AON', 'SanFrancisco.TaxAllocRevRefBonds.1999A.AON', 'CorvallisCity.OR.GOBonds.1999A.AON',
                'Ft.Wayne.SewageWorksJrRevBonds.98B.AON', 'PinellasCty.TranspRevBonds.1998', 'NorthKCHospital.1998.AON', 'Ft.Lauderdale.ExciseTax.1998C.AON',
                'AlbanyAirport.98C.AON', 'AlbanyAirport.98B.AON', 'Minn-St.PaulMetroAirport.Series13.AON', 'Tennessee.GO.1998B.AON',
                'VolusiaCnty.FL.Series1998.AON', 'Portland.Sewer.1998A.AON', 'Pittsburgh.GO.98E.TAXABLE.MBM',
                'Pittsburgh.GO.98D.MBM', 'TennesseeStateSchoolBondAuthority.98SeriesA', 'TennesseeStateSchoolBondAuthority.98SeriesBTAXABLE',
                'Ft.Lauderdale.ExciseTax.1998.AON', 'Ft.Lauderdale.GO.1998.MBM', 'SarasotaMemorialHospital.98A.AON', 'SanFranciscoRDA.98D.CIBS.AON',
                'SanFranciscoRDA.98D.CABS.AON', 'Portland.1998A.AON', 'PittsburghWaterAndSewer.SeriesA.MBM', 'PittsburghWaterAndSewer.SeriesB.MBM',
                'PittsburghWaterAndSewer.SeriesC.MBM', 'Pittsburgh.1998TaxableGOBonds.MBM', '1997.Pittsburgh.GOBonds']
    aIPatten = ['Lincoln.NE.Swr.RBs.03.AON', 'Lincoln.NE.GOs.03.AON',
                'GreenvilleASD.GO.02A.AON', 'AbingtonSD.GOs.02.AON', 'Bedford.Twp.GOs.02.AON']
    allValue = dict()
    if fileTitle == 'Montgomery.ASD.GOs.01.MBM':
        allValue = get_results_pattern6(fileTitle, dataFilePath, localTextFile)
    elif fileTitle in pattern7:
        allValue = get_results_pattern7(fileTitle, dataFilePath, localTextFile)
    elif fileTitle in aIPatten:
        allValue = get_results_pattern2(fileTitle, dataFilePath, localTextFile)
    elif site in pattern1:
        allValue = get_results_pattern1(fileTitle, dataFilePath, localTextFile)
        if allValue['auctionDate'].startswith('Auction Type'):
            allValue = get_results_pattern2(
                fileTitle, dataFilePath, localTextFile)
    elif site in pattern2:
        allValue = get_results_pattern2(fileTitle, dataFilePath, localTextFile)
    elif site in pattern3:
        allValue = get_results_pattern3(fileTitle, dataFilePath, localTextFile)
    elif site in pattern4:
        allValue = get_results_pattern4(fileTitle, dataFilePath, localTextFile)
    elif site in pattern5:
        allValue = get_results_pattern5(fileTitle, dataFilePath, localTextFile)
    return allValue


def get_all_local_text(dataFilePath):
    fileList = os.listdir(dataFilePath)
    localTextFile = {}
    for fname in fileList:
        file = []
        if ".txt" in fname:
            fileName = os.path.join(dataFilePath, fname)
            with open(fileName, 'r') as f:
                for line in f:
                    line = line.strip()
                    file.append(line)
            localTextFile[fileName] = file
    return localTextFile


def init_results_value():
    allValue = dict()
    allValue['auctionDate'] = ''
    allValue['types'] = ''
    allValue['start'] = ''
    allValue['end'] = ''
    allValue['lastUpdate'] = ''
    allValue['status'] = ''
    allValue['principal'] = ''
    allValue['issuer'] = ''
    allValue['description'] = ''
    allValue['bestAONBidder'] = ''
    allValue['bestAONTIC'] = ''
    allValue['bestMBMTIC'] = ''
    allValue['notice'] = ''
    allValue['form'] = ''
    allValue['note'] = ''
    allValue['auctionClosedNotice'] = ''
    allValue['statement'] = ''
    allValue['termIssuer'] = ''
    allValue['termState'] = ''
    allValue['termAmount'] = ''
    allValue['termType'] = ''
    allValue['termRating'] = ''
    allValue['termBankQualified'] = ''
    allValue['termGoodFaith'] = ''
    allValue['termSaleDate'] = ''
    allValue['termDatedDate'] = ''
    allValue['termSettlementDate'] = ''
    allValue['termSaleTime'] = ''
    allValue['termInterestDue'] = ''
    allValue['termPrincipalDue'] = ''
    allValue['termFirstInterestDate'] = ''
    allValue['termCallDates'] = ''
    allValue['termBonds'] = ''
    allValue['termMinBidPrice'] = ''
    allValue['termBidDetails'] = ''
    allValue['termInsurance'] = ''
    allValue['termOtherDetails'] = ''
    allValue['termBidFormat'] = ''
    allValue['termAuctionFormat'] = ''
    allValue['termAwardBasis'] = ''
    allValue['termTwoMinuteRule'] = ''
    allValue['termBondCounsel'] = ''
    allValue['termWebSite'] = ''
    allValue['termContact'] = ''
    allValue['termStatement'] = ''
    return allValue


def get_term_result(allValue, termName, localTextFile):
    if termName in localTextFile:
        tText = localTextFile[termName]
        for line in tText:
            currentIndex = tText.index(line)
            line = line.strip()
            if line == 'Issuer':
                termIssuer = tText[currentIndex+1]
                allValue['termIssuer'] = termIssuer
            elif line == 'State':
                termState = tText[currentIndex+1]
                allValue['termState'] = termState
            elif line == 'Amount':
                if tText[currentIndex+1].startswith('1'):
                    termAmount = tText[currentIndex+2]
                else:
                    termAmount = tText[currentIndex+1]
                allValue['termAmount'] = termAmount
            elif line == 'Type':
                i = currentIndex+2
                termType = ''
                while tText[i].startswith('Bank') is False and tText[i].startswith('Sale Date'):
                    termType = termType + tText[i] + '\n'
                    i += 1
                allValue['termType'] = termType
            elif line == 'Rating':
                termRating = tText[currentIndex+1]
                allValue['termRating'] = termRating
            elif line == 'Bank':
                termBankQualified = tText[currentIndex+2]
                allValue['termBankQualified'] = termBankQualified
            elif line == 'Good Faith':
                termGoodFaith = tText[currentIndex+1]
                allValue['termGoodFaith'] = termGoodFaith
            elif line == 'Sale Date':
                termSaleDate = tText[currentIndex+1]
                allValue['termSaleDate'] = termSaleDate
            elif line == 'Dated Date':
                termDatedDate = tText[currentIndex+1]
                allValue['termDatedDate'] = termDatedDate
            elif line == 'Settlement':
                termSettlementDate = tText[currentIndex+3]
                allValue['termSettlementDate'] = termSettlementDate
            elif line == 'Sale Time':
                termSaleTime = tText[currentIndex+1]
                allValue['termSaleTime'] = termSaleTime
            elif line == 'Interest Due':
                termInterestDue = tText[currentIndex+1]
                allValue['termInterestDue'] = termInterestDue
            elif line == 'Principal Due':
                termPrincipalDue = tText[currentIndex+1]
                allValue['termPrincipalDue'] = termPrincipalDue
            elif line == 'First Interest':
                termFirstInterestDate = tText[currentIndex+2]
                allValue['termFirstInterestDate'] = termFirstInterestDate
            elif line == 'Call Dates':
                termCallDates = tText[currentIndex+1]
                allValue['termCallDates'] = termCallDates
            elif line == 'Term Bonds':
                termBonds = tText[currentIndex+1]
                allValue['termBonds'] = termBonds
            elif line == 'Min. Bid Price':
                termMinBidPrice = tText[currentIndex+1]
                allValue['termMinBidPrice'] = termMinBidPrice
            elif line == 'Bid Details':
                i = currentIndex+1
                termBidDetails = ''
                while tText[i].startswith('Insurance') is False:
                    termBidDetails = termBidDetails + tText[i] + '\n'
                    i += 1
                allValue['termBidDetails'] = termBidDetails
            elif line == 'Insurance':
                termInsurance = tText[currentIndex+1]
                allValue['termInsurance'] = termInsurance
            elif line == 'Other Details':
                i = currentIndex+1
                termOtherDetails = ''
                while tText[i].startswith('Bid Format') is False:
                    termOtherDetails = termOtherDetails + tText[i] + '\n'
                    i += 1
                allValue['termOtherDetails'] = termOtherDetails
            elif line == 'Bid Format':
                termBidFormat = tText[currentIndex+1]
                allValue['termBidFormat'] = termBidFormat
            elif line == 'Auction Format':
                termAuctionFormat = tText[currentIndex+1]
                allValue['termAuctionFormat'] = termAuctionFormat
            elif line == 'Award Basis':
                termAwardBasis = tText[currentIndex+1]
                allValue['termAwardBasis'] = termAwardBasis
            elif line == 'Two-Minute Rule':
                termTwoMinuteRule = tText[currentIndex+1]
                allValue['termTwoMinuteRule'] = termTwoMinuteRule
            elif line == 'Bond Counsel':
                i = currentIndex+1
                termBondCounsel = ''
                while tText[i].startswith('Web') is False:
                    if tText[i].startswith('Terms as of'):
                        termBondCounsel = ''
                        break
                    else:
                        termBondCounsel = termBondCounsel + tText[i] + '\n'
                    i += 1
                allValue['termBondCounsel'] = termBondCounsel
            elif line.startswith('Web'):
                termWebSite = tText[currentIndex+2]
                allValue['termWebSite'] = termWebSite
            elif line == 'Contact':
                i = currentIndex+1
                termContact = ''
                while tText[i].startswith('Terms as of') is False:
                    termContact = termContact + tText[i] + '\n'
                    i += 1
                allValue['termContact'] = termContact
            elif line.startswith('Terms as of'):
                i = currentIndex+1
                termStatement = ''
                while tText[i].startswith('[') is False:
                    termStatement = termStatement + tText[i] + '\n'
                    i += 1
                allValue['termStatement'] = termStatement
    return allValue


def get_results_pattern1(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Date':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
            elif line == 'Type':
                types = text[currentIndex+1]
                allValue['types'] = types
            elif line == 'Start':
                start = text[currentIndex+2]
                allValue['start'] = start
            elif line == 'End':
                end = text[currentIndex+2]
                allValue['end'] = end
            elif line == 'Last Update':
                lastUpdate = text[currentIndex+1]
                allValue['lastUpdate'] = lastUpdate
            elif line == 'Status':
                status = text[currentIndex+1]
                allValue['status'] = status
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
            elif line == 'NOTICE:':
                notice = 'NOTICE: '+text[currentIndex+1]
                allValue['notice'] = notice
            elif line == 'Note:':
                note = 'Note: '+text[currentIndex+1]
                allValue['note'] = note
            elif line.startswith('1st'):
                bestAONBidder = text[currentIndex+2]
                bestAONTIC = text[currentIndex+3]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
            elif re.match(r'\$\d*', line) is not None and text[currentIndex+1] == '*' and 'Preliminary' not in text[currentIndex+2]:
                principal = text[currentIndex]
                allValue['principal'] = principal
                issuer = text[currentIndex+2]
                allValue['issuer'] = issuer
                i = currentIndex + 3
                description = ''
                while 'Bidder' not in text[i] and 'Best' not in text[i]:
                    if 'Preliminary' in text[i]:
                        description = ''
                        break
                    description = description+text[i]+'\n'
                    i += 1
                allValue['description'] = description
            elif line == 'Bidder':
                i = currentIndex
                form = ''
                while 'Preliminary' not in text[i] and 'Click below' not in text[i] and 'Bid not'not in text[i]:
                    if text[i] in ['1st', '2nd', '3rd'] or re.match(r'\d+th', text[i]) is not None:
                        form = form+'\n'+text[i]
                    else:
                        form = form+'| '+text[i]
                    i += 1
                allValue['form'] = form
            elif line.startswith('*Preliminary') or line.startswith('*Bid not') or line.startswith('Preliminary'):
                statement = text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i] and 'Go to:' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('‡') or text[currentIndex+i].startswith('**'):
                        statement = statement+'\n'+text[currentIndex+i]
                    i += 1
                allValue['statement'] = statement
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def get_results_pattern2(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Status':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
                types = text[currentIndex+2]
                allValue['types'] = types

                i = currentIndex+3
                if text[i].startswith('var'):
                    i += 1
                start = text[i]
                allValue['start'] = start
                i += 1
                if text[i].startswith('var'):
                    i += 1
                end = text[i]
                allValue['end'] = end
                i += 1
                if text[i].startswith('var'):
                    i += 1
                lastUpdate = text[i]
                i += 1
                if text[i].startswith('EDT'):
                    lastUpdate = lastUpdate+' '+text[i]
                    i += 1
                allValue['lastUpdate'] = lastUpdate
                status = text[i]
                allValue['status'] = status
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
            elif line == 'NOTICE:':
                notice = 'NOTICE: '+text[currentIndex+1]
                allValue['notice'] = notice
            elif line == 'Note:':
                note = 'Note: '+text[currentIndex+1]
                allValue['note'] = note
            elif re.match(r'\$\d*', line) is not None and text[currentIndex+1] == '*':
                principal = text[currentIndex]
                allValue['principal'] = principal
                issuer = text[currentIndex+2]
                allValue['issuer'] = issuer
                i = currentIndex + 3
                description = ''
                while text[i].startswith('Best AON Bidder') is False:
                    description = description+text[i]+'\n'
                    i += 1
                allValue['description'] = description
            elif line.startswith('Best AON Bidder:') and text[currentIndex+2].startswith('Best MBM TIC:'):
                bestAONBidder = text[currentIndex+3] + \
                    '\n' + text[currentIndex+4]
                bestAONTIC = text[currentIndex+5] + '\n' + text[currentIndex+6]
                bestMBMTIC = text[currentIndex+7] + '\n' + text[currentIndex+8]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
                allValue['bestMBMTIC'] = bestMBMTIC
            elif line.startswith('Best AON Bidder:') and text[currentIndex+2].startswith('Best MBM TIC:') is False:
                bestAONBidder = text[currentIndex+2]
                bestAONTIC = text[currentIndex+3]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
            elif line == 'Bidder':
                if text[currentIndex-1].startswith('Rank') is False:
                    i = 0
                    form = ''
                    while 'Best AON' not in text[currentIndex+i]:
                        if i % 3 == 0:
                            form = form+'\n'+text[currentIndex+i]
                        else:
                            form = form+'| '+text[currentIndex+i]
                        i += 1
                    while '*Preliminary' not in text[currentIndex+i] and ' Bidder' not in text[currentIndex+i] and \
                            'Note:'not in text[currentIndex+i] and 'Go to:'not in text[currentIndex+i] and '**Winner'not in text[currentIndex+i]:
                        if text[currentIndex+i] in ['Best AON', 'Cover AON']:
                            form = form+'\n'+text[currentIndex+i]
                        else:
                            form = form+'| '+text[currentIndex+i]
                        i += 1
                else:
                    i = currentIndex-1
                    form = ''
                    while '*Preliminary' not in text[i] and ' Bidder' not in text[i] and 'Note:'not in text[i] and 'Go to:'not in text[i] and '**Winner'not in text[i]:
                        if text[i] in ['1st', '2nd', '3rd', 'Best AON', 'Cover AON'] or re.match(r'\d+th', text[i]) is not None:
                            form = form+'\n'+text[i]
                        else:
                            form = form+'| '+text[i]
                        i += 1
                allValue['form'] = form
            elif line.startswith('*Preliminary') or line.startswith(' Bidder') or line.startswith('**Winner'):
                statement = text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i] and 'Go to:' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('‡') or text[currentIndex+i].startswith('**'):
                        statement = statement+'\n'+text[currentIndex+i]
                    i += 1
                allValue['statement'] = statement
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def get_results_pattern3(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Status':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
                types = text[currentIndex+2]
                allValue['types'] = types
                start = text[currentIndex+3]
                allValue['start'] = start
                end = text[currentIndex+4]
                allValue['end'] = end
                lastUpdate = text[currentIndex+5]
                allValue['lastUpdate'] = lastUpdate
                status = text[currentIndex+6]
                allValue['status'] = status
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
            elif line == 'NOTICE:':
                notice = 'NOTICE: '+text[currentIndex+1]
                allValue['notice'] = notice
            elif line == 'Note:':
                note = 'Note: '+text[currentIndex+1]
                allValue['note'] = note
            elif re.match(r'\$\d*', line) is not None and text[currentIndex+1] == '*':
                principal = text[currentIndex]
                allValue['principal'] = principal
                issuer = text[currentIndex+2]
                allValue['issuer'] = issuer
                i = currentIndex + 3
                description = ''
                while text[i].startswith('Best AON Bidder') is False:
                    description = description+text[i]+'\n'
                    i += 1
                allValue['description'] = description
            elif line.startswith('Best AON Bidder:') and text[currentIndex+2].startswith('Best MBM TIC:'):
                bestAONBidder = text[currentIndex+3] + \
                    '\n' + text[currentIndex+4]
                bestAONTIC = text[currentIndex+5] + '\n' + text[currentIndex+6]
                bestMBMTIC = text[currentIndex+7] + '\n' + text[currentIndex+8]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
                allValue['bestMBMTIC'] = bestMBMTIC
            elif line.startswith('Best AON Bidder:') and text[currentIndex+2].startswith('Best MBM TIC:') is False:
                bestAONBidder = text[currentIndex+2]
                bestAONTIC = text[currentIndex+3]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
            elif line == 'Bidder':
                if text[currentIndex-1].startswith('Rank') is False:
                    i = 0
                    form = ''
                    while 'Best AON' not in text[currentIndex+i]:
                        if i % 7 == 0:
                            form = form+'\n'+text[currentIndex+i]
                        else:
                            form = form+'| '+text[currentIndex+i]
                        i += 1
                    while '*Preliminary' not in text[currentIndex+i]:
                        if text[currentIndex+i] in ['Best AON', 'Cover AON']:
                            form = form+'\n'+text[currentIndex+i]
                        else:
                            form = form+'| '+text[currentIndex+i]
                        i += 1
                else:
                    i = currentIndex-1
                    form = ''
                    while '*Preliminary' not in text[i]:
                        if text[i] in ['1st', '2nd', '3rd', 'Best AON', 'Cover AON'] or re.match(r'\d+th', text[i]) is not None:
                            form = form+'\n'+text[i]
                        else:
                            form = form+'| '+text[i]
                        i += 1
                allValue['form'] = form
            elif line.startswith('*Preliminary'):
                statement = text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('‡') or text[currentIndex+i].startswith('**'):
                        statement = statement+'\n'+text[currentIndex+i]
                    i += 1
                allValue['statement'] = statement
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def get_results_pattern4(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Status':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
                types = text[currentIndex+2]
                allValue['types'] = types
                start = text[currentIndex+3]
                allValue['start'] = start
                end = text[currentIndex+4]
                allValue['end'] = end
                lastUpdate = text[currentIndex+5]
                allValue['lastUpdate'] = lastUpdate
                status = text[currentIndex+6]
                allValue['status'] = status
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
            elif line == 'NOTICE:':
                notice = 'NOTICE: '+text[currentIndex+1]
                allValue['notice'] = notice
            elif line == 'Note:':
                note = 'Note: '+text[currentIndex+1]
                allValue['note'] = note
            elif re.match(r'\$\d*', line) is not None and text[currentIndex+1] == '*':
                principal = text[currentIndex]
                allValue['principal'] = principal
                issuer = text[currentIndex+2]
                allValue['issuer'] = issuer
                i = currentIndex + 3
                description = ''
                while text[i].startswith('Best MBM TIC') is False:
                    description = description+text[i]+'\n'
                    i += 1
                allValue['description'] = description
            elif line.startswith('Best MBM TIC:'):
                bestMBMTIC = text[currentIndex+1]
                allValue['bestMBMTIC'] = bestMBMTIC
            elif line == 'Sep 1, 2002':
                i = 0
                form = 'Due| Principal Amount*| Coupon| Purchas| Price| Purchase Yield| MBM Winner**| Time'
                while 'Preliminary,' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('Sep'):
                        form = form+'\n'+text[currentIndex+i]
                    else:
                        form = form+'| '+text[currentIndex+i]
                    i += 1
                allValue['form'] = form
            elif line.startswith('Preliminary,'):
                statement = '*'+text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('‡') or text[currentIndex+i].startswith('**'):
                        statement = statement+'\n'+text[currentIndex+i]
                    i += 1
                allValue['statement'] = statement
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def get_results_pattern5(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Date':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
            elif line == 'Type':
                types = text[currentIndex+1]
                allValue['types'] = types
            elif line == 'Start':
                start = text[currentIndex+2]
                allValue['start'] = start
            elif line == 'End':
                end = text[currentIndex+2]
                allValue['end'] = end
            elif line == 'Last Update':
                lastUpdate = text[currentIndex+1]
                allValue['lastUpdate'] = lastUpdate
            elif line == 'Status':
                status = text[currentIndex+1]
                allValue['status'] = status
                if text[currentIndex+2] == 'NOTICE:':
                    i = currentIndex + 3
                    notice = 'NOTICE: '
                    while text[i].startswith('$') is False:
                        notice = notice + text[i]
                        i += 1
                    allValue['notice'] = notice
                    principal = text[i]
                    allValue['principal'] = principal
                    if text[i+1].startswith('*'):
                        issuer = text[i+2]
                        i = i+3
                    else:
                        issuer = text[i+1]
                        i = i+2
                    allValue['issuer'] = issuer
                    description = ''
                    while text[i].startswith('Bidder') is False:
                        description = description+text[i]+'\n'
                        i += 1
                    allValue['description'] = description
                else:
                    principal = text[currentIndex+2]
                    allValue['principal'] = principal
                    i = currentIndex+3
                    if text[i].startswith('*'):
                        i += 1
                    issuer = text[i]
                    allValue['issuer'] = issuer
                    i = i+1
                    description = ''
                    while text[i].startswith('Bidder') is False:
                        description = description+text[i]+'\n'
                        i += 1
                    allValue['description'] = description
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
                bestAONBidder = text[currentIndex+2]
                bestAONTIC = text[currentIndex+3]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
            elif line == 'Bidder':
                i = currentIndex
                form = ''
                while 'Note:' not in text[i] and 'Bid not submitted' not in text[i] and 'Click below ' not in text[i]:
                    if text[i] in ['1st', '2nd', '3rd'] or re.match(r'\d+th', text[i]) is not None:
                        form = form+'\n'+text[i]
                    else:
                        form = form+'| '+text[i]
                    i += 1
                allValue['form'] = form
            elif line.startswith('1st'):
                bestAONBidder = text[currentIndex+2]
                bestAONTIC = text[currentIndex+3]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
            elif line.startswith('Note:') or line.startswith('†'):
                note = text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i]:
                    note = note + ' '+text[currentIndex+i]
                    i += 1
                allValue['note'] = note
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def get_results_pattern6(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Status':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
                types = text[currentIndex+2]
                allValue['types'] = types
                start = text[currentIndex+3]
                allValue['start'] = start
                end = text[currentIndex+4]
                allValue['end'] = end
                lastUpdate = text[currentIndex+5]
                allValue['lastUpdate'] = lastUpdate
                status = text[currentIndex+6]
                allValue['status'] = status
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
            elif line == 'NOTICE:':
                notice = 'NOTICE: '+text[currentIndex+1]
                allValue['notice'] = notice
            elif line == 'Note:':
                note = 'Note: '+text[currentIndex+1]
                allValue['note'] = note
            elif re.match(r'\$\d*', line) is not None and text[currentIndex+1] == '*':
                principal = text[currentIndex]
                allValue['principal'] = principal
                issuer = text[currentIndex+2]
                allValue['issuer'] = issuer
                i = currentIndex + 3
                description = ''
                while text[i].startswith('Best MBM TIC') is False:
                    description = description+text[i]+'\n'
                    i += 1
                allValue['description'] = description
            elif line.startswith('Best AON Bidder:'):
                bestMBMTIC = text[currentIndex+2] + ' '+text[currentIndex+3]
                allValue['bestMBMTIC'] = bestMBMTIC
                bestAONTIC = text[currentIndex+4] + ' '+text[currentIndex+5]
                bestAONBidder = text[currentIndex+6] + ' '+text[currentIndex+7]
                allValue['bestAONBidder'] = bestAONBidder
                allValue['bestAONTIC'] = bestAONTIC
            elif line == 'Sep 1, 2002':
                i = 0
                form = 'Due| Principal Amount*| Coupon| Purchas| Price| Purchase Yield| MBM Winner**| Time'
                while 'Preliminary,' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('Sep'):
                        form = form+'\n'+text[currentIndex+i]
                    else:
                        form = form+'| '+text[currentIndex+i]
                    i += 1
                allValue['form'] = form
            elif line.startswith('Preliminary,'):
                statement = '*'+text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('‡') or text[currentIndex+i].startswith('**'):
                        statement = statement+'\n'+text[currentIndex+i]
                    i += 1
                allValue['statement'] = statement
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def get_results_pattern7(fileTitle, dataFilePath, localTextFile):
    allValue = init_results_value()
    fileName = dataFilePath+fileTitle+'_summary.txt'
    termName = dataFilePath+fileTitle+'_terms.txt'
    if fileName in localTextFile:
        text = localTextFile[fileName]
        for currentIndex, line in enumerate(text):
            line = line.strip()
            if line == 'Auction Status':
                auctionDate = text[currentIndex+1]
                allValue['auctionDate'] = auctionDate
                types = text[currentIndex+2]
                allValue['types'] = types
                start = text[currentIndex+3]
                allValue['start'] = start
                end = text[currentIndex+4]
                allValue['end'] = end
                lastUpdate = text[currentIndex+5]
                allValue['lastUpdate'] = lastUpdate
                status = text[currentIndex+6]
                allValue['status'] = status
            elif line.startswith('Auction Closed At:'):
                auctionClosed = text[currentIndex]
                allValue['auctionClosedNotice'] = auctionClosed
            elif line == 'NOTICE:':
                notice = 'NOTICE: '+text[currentIndex+1]
                allValue['notice'] = notice
            elif line == 'Note:':
                note = 'Note: '+text[currentIndex+1]
                allValue['note'] = note
            elif re.match(r'\$\d*', line) is not None and text[currentIndex+1] == '*' and 'Preliminary' not in text[currentIndex+2]:
                principal = text[currentIndex]
                allValue['principal'] = principal
                issuer = text[currentIndex+2]
                allValue['issuer'] = issuer
                i = currentIndex + 3
                description = ''
                while text[i].startswith('Best ') is False:
                    description = description+text[i]+'\n'
                    i += 1
                allValue['description'] = description
            elif line == 'Winner**:':
                if text[currentIndex-1] == 'Best MBM TIC:':
                    bestAONBidder = text[currentIndex+1] +\
                        ' '+text[currentIndex+2]
                    bestAONTIC = text[currentIndex+3] +\
                        ' '+text[currentIndex+4]
                    bestMBMTIC = text[currentIndex+5] +\
                        ' '+text[currentIndex+6]
                    allValue['bestMBMTIC'] = bestMBMTIC
                    allValue['bestAONBidder'] = bestAONBidder
                    allValue['bestAONTIC'] = bestAONTIC
                    form = 'Due| Principal Amount*| Serial Sinker/Term| Coupon'
                    i = currentIndex + 16
                    j = 0
                    while 'Preliminary,' not in text[i]:
                        if j % 4 == 0:
                            form = form + '\n' + text[i]
                        else:
                            form = form + '| ' + text[i]
                        j += 1
                        i += 1
                    allValue['form'] = form
                elif text[currentIndex-1] == 'Best AON Bidder:':
                    bestMBMTIC = text[currentIndex+1] +\
                    ' '+text[currentIndex+2]
                    bestAONTIC = text[currentIndex+3] +\
                    ' '+text[currentIndex+4]
                    bestAONBidder = text[currentIndex+5] +\
                    ' '+text[currentIndex+6]
                    allValue['bestMBMTIC'] = bestMBMTIC
                    allValue['bestAONBidder'] = bestAONBidder
                    allValue['bestAONTIC'] = bestAONTIC
                    form = 'Due| Principal Amount*| Coupon| Purchas| Price| Purchase Yield| MBM Winner**'
                    i = currentIndex + 18
                    j = 0
                    while 'Preliminary,' not in text[i]:
                        if j % 6 == 0:
                            form = form + '\n' + text[i]
                        else:
                            form = form + '| ' + text[i]
                        j += 1
                        i += 1
                    allValue['form'] = form
            elif line.startswith('Preliminary,'):
                statement = '*'+text[currentIndex]
                i = 1
                while 'Click below to see other bidder results' not in text[currentIndex+i]:
                    if text[currentIndex+i].startswith('‡') or text[currentIndex+i].startswith('**'):
                        statement = statement+'\n'+text[currentIndex+i]
                    i += 1
                allValue['statement'] = statement
        allValue = get_term_result(allValue, termName, localTextFile)
    return allValue


def writeFianlResults(resultPageFile, dataFilePath, outputFile):
    localTextFile = get_all_local_text(dataFilePath)
    xlsFile = xlwt.Workbook()
    sheet1 = xlsFile.add_sheet('results', cell_overwrite_ok=True)

    header = ['Id', 'Auction Name', 'Date', 'Principal', 'Issuer', 'State', 'Site', 'Description', 'Summary link',
              'Term link', 'Auction Date', 'Auction Types', 'Auction Start', 'Auction End', 'Auction Last Update', 'Auction Status',
              'Auction Principal', 'Auction Issuer', 'Auction Description', 'Auction Best AON Bidder', 'Auction Best AON TIC',
              'Auction Best MBM TIC', 'Auction Notice', 'Auction Form', 'Auction Note', 'Auction Closed Notice', 'Auction Statement',
              'Term Issuer', 'Term State', 'Term Amount', 'Term Type', 'Term Rating', 'Term Bank Qualified', 'Term Good Faith',
              'Term Sale Date', 'Term Dated Date', 'Term Settlement Date', 'Term Sale Time', 'Term Interest Due', 'Term Principal Due',
              'Term First Interest Date', 'Term Call Dates', 'Term Bonds', 'Term Min. Bid Price', 'Term Bid Details', 'Term Insurance',
              'Term OtherDetails', 'Term BidFormat', 'Term AuctionFormat', 'Term AwardBasis', 'Term TwoMinuteRule', 'Term BondCounsel',
              'Term WebSite', 'Term Contact', 'Term Statement']

    for i in range(0, len(header)):
        sheet1.write(0, i, header[i])

    with open(resultPageFile, 'r') as rp:
        par = tqdm.tqdm()
        i = 1
        for line in rp:
            tokens = line.split('\t')
            fileTitle = tokens[1]
            par.update(1)
            site = tokens[6]
            print(fileTitle)
            allValue = get_encode_pattern(
                site, fileTitle, dataFilePath, localTextFile)
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
    linkFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/html/'
    dataFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/text/'
    resultPageFile = linkFilePath+'results_page_info.tsv'
    url = 'https://auctions.grantstreet.com/results/bond'
    webPage = get_all_trs(url)
    outputFile = linkFilePath + 'final_bonds.xls'
    get_results_page_info(webPage, resultPageFile, dataFilePath)
    writeFianlResults(resultPageFile, dataFilePath, outputFile)



if __name__ == "__main__":
    main()

'''
linkFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/html/'
dataFilePath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/fiscal_advisor/text/'
resultPageFile = linkFilePath+'results_page_info.tsv'
url = 'https://auctions.grantstreet.com/results/bond'
fileTitle = 'GreenvilleASD.GO.02A.AON'
localTextFile = get_all_local_text(dataFilePath)
alls = get_results_pattern2(fileTitle, dataFilePath, localTextFile)
print(alls)
'''