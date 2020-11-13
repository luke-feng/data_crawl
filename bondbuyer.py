import requests
from bs4 import BeautifulSoup
import re
import tqdm
import fiscal_advisors as fa


def gen_url(startUrl, id):
    return startUrl+str(id)


def get_page(url):
    webPage = requests.get(url)
    if webPage.status_code == 404:
        return None
    else:
        page = webPage.text
        page = page.replace('</br>', '\n')
        return page


def get_id(tagId):
    Id = re.search(r'\d+', tagId)
    if Id is not None:
        return Id.group(0)


def get_all_ids(results):
    Ids = []
    for result in results:
        tagId = result['id']
        Ids.append(get_id(tagId))
    return Ids


def get_details(filePath, webPage):
    soup = BeautifulSoup(webPage, 'lxml')
    head = soup.find('p', 'Headlinecls').get_text()
    if head is not None:
        fileName = filePath + head+'.txt'
        with open(fileName, 'w') as out:
            salesResults = soup.find_all('p', 'RCSalesResultcls')
            if len(salesResults) > 0:
                tblExcel = soup.find_all('table', 'tblExcel')
                tblExcelHide = soup.find_all('table', 'tblExcelHide')
                footRCSalesResult = soup.find_all('p', 'FootRCSalesResultcls')

                srIds = get_all_ids(salesResults)
                teIds = get_all_ids(tblExcel)
                tehIds = get_all_ids(tblExcelHide)
                frIds = get_all_ids(footRCSalesResult)
                for id in srIds:
                    if id in teIds and id in frIds:
                        srP = srIds.index(id)
                        teP = teIds.index(id)
                        frP = frIds.index(id)
                        out.write('======RCSalesResultcls======\n')
                        out.write(salesResults[srP].get_text(separator='\n'))
                        out.write('\n')
                        out.write('======tblExcel======\n')
                        out.write(tblExcel[teP].get_text(separator='\n'))
                        out.write('\n')
                        out.write('======FootRCSalesResultcls======\n')
                        out.write(
                            footRCSalesResult[frP].get_text(separator='\n'))
                        out.write('\n')
                    elif id in tehIds and id in frIds:
                        srP = srIds.index(id)
                        teP = tehIds.index(id)
                        frP = frIds.index(id)
                        out.write('======RCSalesResultcls======\n')
                        out.write(salesResults[srP].get_text(separator='\n'))
                        out.write('\n')
                        out.write('======tblExcel======\n')
                        out.write(tblExcelHide[teP].get_text(separator='\n'))
                        out.write('\n')
                        out.write('======FootRCSalesResultcls======\n')
                        out.write(
                            footRCSalesResult[frP].get_text(separator='\n'))
                        out.write('\n')
                    else:
                        print('index error')
            else:
                productDataPrev = soup.select(
                    '#productDataPrev')[0].get_text(separator='\n')
                out.write(productDataPrev)
        out.close()
        return head


def get_webpage_to_local(startUrl, path, infoPageName):
    count = 0
    startId = 9999
    par = tqdm.tqdm(total=startId, ncols=80)
    Id = startId
    with open(infoPageName, 'w') as iP:
        iP.write('ID' + '\t'+'Page Name' + '\t' + 'Summary link' + '\n')
        while Id > 0:
            par.update(1)
            url = gen_url(startUrl, Id)
            page = get_page(url)
            if page is not None:
                head = get_details(path, page)
                count += 1
                iP.write(str(Id) + '\t'+head + '\t' + url + '\n')
            Id -= 1
    iP.close()
    print('total page is {}'.format(str(count)))


startUrl = 'https://data.bondbuyer.com/salesresults/GetDetails/'
textPath = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/bondbuyer/text/'
resultPath =  '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/bondbuyer/result/'
infoPageName = resultPath + 'infoPage.tsv'
get_webpage_to_local(startUrl, textPath, infoPageName)

usState = ['ALABAMA', 'ALASKA', 'ARIZONA', 'ARKANSAS', 'CALIFORNIA', 'COLORADO',
           'CONNECTICUT', 'DELAWARE', 'FLORIDA', 'GEORGIA', 'HAWAII', 'IDAHO',
           'ILLINOIS', 'INDIANA', 'IOWA', 'KANSAS', 'KENTUCKY', 'LOUISIANA', 'MAINE',
           'MARYLAND', 'MASSACHUSETTS', 'MICHIGAN', 'MINNESOTA', 'MISSISSIPPI', 'MISSOURI',
           'MONTANA', 'NEBRASKA', 'NEVADA', 'NEW HAMPSHIRE', 'NEW JERSEY', 'NEW MEXICO',
           'NEW YORK', 'NORTH CAROLINA', 'NORTH DAKOTA', 'OHIO', 'OKLAHOMA', 'OREGON',
           'PENNSYLVANIA', 'RHODE ISLAND', 'SOUTH CAROLINA', 'SOUTH DAKOTA', 'TENNESSEE',
           'TEXAS', 'UTAH', 'VERMONT', 'VIRGINIA', 'WASHINGTON', 'WEST VIRGINIA', 'WISCONSIN', 'WYOMING']


#def init_resule_value():


