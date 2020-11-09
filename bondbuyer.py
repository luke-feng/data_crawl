import requests
from bs4 import BeautifulSoup
import re
import tqdm


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


'''startUrl = 'https://data.bondbuyer.com/salesresults/GetDetails/'
startId = 4802
Id = startId
url = gen_url(startUrl, Id)
page = get_page(url)
page = page.replace('</br>', '\n')
soup = BeautifulSoup(page, 'lxml')
salesResults = soup.find_all('p', 'RCSalesResultcls')
print(len(salesResults))'''


def main():
    startUrl = 'https://data.bondbuyer.com/salesresults/GetDetails/'
    startId = 9999
    Id = startId
    path = '/Users/chaofeng/Documents/GitHub/data_crawl/raw_data/bondbuyer/'
    count = 0
    par = tqdm.tqdm(total = startId, ncols=80)
    while Id > 0:
        par.update(1)
        url = gen_url(startUrl, Id)
        page = get_page(url)
        if page is not None:
            get_details(path, page)
            count += 1
        else:
            print('page {} is not exist'.format(str(Id)))
        Id -= 1
    print('total page is {}'.format(str(count)))


if __name__ == "__main__":
    main()

