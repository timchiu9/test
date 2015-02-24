# -*- coding: utf-8 -*-
import requests, time, re, os, logging
from bs4 import BeautifulSoup
from random import randint

url='http://class.ruten.com.tw/category/sub00.php?c=001200070004' #還要改category
pageurl= url+'&p=1&p=%d'

header = {
'Cookie':'ruten_ad_20150108-122732_expire=Tue%2C%2003%20Feb%202015%2006%3A39%3A18%20GMT; ruten_ad_20150108-122732=1; ruten_ad_20150130-164849_expire=Tue%2C%2003%20Feb%202015%2006%3A39%3A48%20GMT; ruten_ad_20150130-164849=1; _ts_id=3D04360E3C083E0D3D; _gat=1; _ga=GA1.3.1515021042.1422859158',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'}

def getItemCode(link): #unicode item code
    m = re.match(r"([^ ]+)show\?(?P<number>.+)", link)
    itemCode = "%s"%(m.group('number'))
    return itemCode

def create_csv(file, csvHeaders):
    csvHeader = ','.join(csvHeaders)
    #建檔案
    item_detail = open(file, 'w')
    #寫入header
    item_detail.write(csvHeader)
    item_detail.write('\n')
    item_detail.close()

    print 'csv file created.'

def append_detail_csv(link, header, file):
    itemCode = getItemCode(link).encode('utf8')

    request_get = requests.get(link, headers=header)
    request_get.encoding = 'big5'
    soup = BeautifulSoup(request_get.text)
    printarea = soup.select('.auction-data')[0]

    #開檔案
    item_detail = open(file, 'a')

    h2 = printarea.select('h2')[0]
    title = h2.text.strip().replace(',', ' ').encode('utf8')

    #------------------------------------
    productMemo = soup.select('.product-memo')[0]

    loc = productMemo.select('.location')[0]
    location = loc.select('.content')[0].text.strip().encode('utf8')

    upload = productMemo.select('.upload-time')[0]
    uploadDate = upload.select('.date')[0].text.strip().encode('utf8')
    uploadTime = upload.select('.time')[0].text.strip().encode('utf8')
    #---------------------------------------
    productAuctionInfo = soup.select('.product-auction-info')[0]

    priceTemp = productAuctionInfo.select('.dollar')[0].text.strip()
    price = ''.join(priceTemp.split(',')).encode('utf8')

    soldCnt = productAuctionInfo.select('.sold-count')[0]
    soldCount = soldCnt.select('.number')[0].text.strip().encode('utf8')

    ship = productAuctionInfo.select('.ship')[0]
    shipFare = ship.select('.cost')[0].text.strip().encode('utf8')

    Id = productAuctionInfo.select('.user-id')[0]
    sellerId = Id.select('a')[0].text.strip().encode('utf8')
    sellerIndex = Id.select('a')[0]['href'].encode('utf8')

    allCredit = productAuctionInfo.select('.all-credit')[0]
    credit = allCredit.select('a')[0].text.strip().encode('utf8')

    item_detail.write(','.join([title, itemCode, location, uploadDate, uploadTime, price, soldCount, shipFare, sellerId, sellerIndex, credit]))
    item_detail.write('\n')
    item_detail.close()

    print 'detail csv file appended.'

#deprecated
def checkSalesRecord(itemCode, header):
    offerLogUrl = 'http://goods.ruten.com.tw/item/history_full.php?%s&page=1#log'%itemCode
    offerLog_res = requests.get(offerLogUrl, headers=header)
    offerLog_res.encoding = 'big5'
    soup = BeautifulSoup(offerLog_res.text)
    offerLog = soup.select('.offer-log')[0]

    if len(offerLog.select('.msg')) == 0:
        return True
    else:
        return False

def getSalesRecord(itemCode, webHeader, file):
    offerLogUrl = 'http://goods.ruten.com.tw/item/history_full.php?'+ itemCode.encode('utf8') +'&page=%d#log' #如何代換其中一個%為已知另一個%維持未知？
    n = 1

    offerLog_res = requests.get(offerLogUrl%n, headers=webHeader)
    offerLog_res.encoding = 'big5'
    soup1 = BeautifulSoup(offerLog_res.text)
    offerLog = soup1.select('.offer-log')[0]

    #建header
    headers = ['出價者', '數量', '日期', '時間']

    #建立只有header的csv file
    create_csv(file, headers)
    # if not os.path.exists(file):
    #     create_csv(file, headers)
    # else:
    #     os.remove(file)
    #     create_csv(file, headers)

    #get sales record
    tr = offerLog.select('tr')[1:]
    for row in tr:
        userId = row.select('.user-id')[0].text.strip().encode('utf8')
        qty = row.findAll('td', {'headers':'quantity'})[0].text.strip().encode('utf8')
        recordDate = row.select('.date')[0].text.strip().encode('utf8')
        recordTime = row.select('.time')[0].text.strip().encode('utf8')
        record = [userId, qty, recordDate, recordTime]

        #開csv檔寫入record
        record_file = open(file, 'a')
        record_file.write(','.join(record))
        record_file.write('\n')
        record_file.close()

    #
    while len(offerLog.select('.msg')) == 0:
        for a in offerLog.select('p')[1].select('a'):
            if u"下" in a.text:
                n += 1
                offerLog_res = requests.get(offerLogUrl%n, headers=webHeader) #下一頁網頁
                offerLog_res.encoding=('big5')
                soup1 = BeautifulSoup(offerLog_res.text)
                offerLog = soup1.select('.offer-log')[0] #取出下一頁offer log
                tr = offerLog.select('tr')[1:]
                for row in tr:
                    userId = row.select('.user-id')[0].text.strip().encode('utf8')
                    qty = row.findAll('td', {'headers':'quantity'})[0].text.strip().encode('utf8')
                    recordDate = row.select('.date')[0].text.strip().encode('utf8')
                    recordTime = row.select('.time')[0].text.strip().encode('utf8')
                    record = [userId, qty, recordDate, recordTime]

                    #開csv檔寫入record
                    record_file = open(file, 'a')
                    record_file.write(','.join(record))
                    record_file.write('\n')
                    record_file.close()
                break #繼續while
        else: #正常執行完for loop才會執行這個區塊?
            break #break while


#算全部頁數
errorcount = 0
while True:
    try:
        res = requests.get(url,headers=header)
        res.encoding=('big5')
        soup = BeautifulSoup(res.text)
        page = int(soup.select('.page-total')[0].text)
        print 'This category has %d pages.'%page
    except Exception, e:
        errorcount += 1
        print 'Error occurred. error %d.'%errorcount
        logging.exception(e)
        continue
    break

#設定開始、結束頁面、抓取頁面間隔、每個檔案抓取頁數
startPageNumber = 1
endPageNumber = page
interval = 1
filePageCount = page

#建立資料夾及檔案
date = '0214'
category = '保養組合'
datailTargetDir = 'item_detail/%s/%s/'%(date, category)
recordTargetDir = 'sales_record/%s/%s/'%(date, category)

if not os.path.exists(datailTargetDir):
    os.makedirs(datailTargetDir)

if not os.path.exists(recordTargetDir):
    os.makedirs(recordTargetDir)

file = datailTargetDir+'items_page_%d_%d_interval%d.csv'%(startPageNumber, startPageNumber+(filePageCount*interval)-1, interval)

#用header建csv檔
itemDetailCsvHeaders = ["物品名稱", "商品編號", "物品所在地", "上架日期", "上架時間", "商品價格", "已賣數量", "運費", "賣家", "賣場首頁", "評價分數"]

create_csv(file, itemDetailCsvHeaders)
# if not os.path.exists(file):
#     create_csv(file, itemDetailCsvHeaders)
# else:
#     os.remove(file)
#     create_csv(file, itemDetailCsvHeaders)

print 'Capture from page %d to %d.'%(startPageNumber, endPageNumber)

for p in range(startPageNumber, endPageNumber+1, interval):
    pageStartTime = int(round(time.time() * 1000)) #time以秒為單位，*1000換成millisec
    errorcount = 0
    while True:
        try:
            if (p-startPageNumber) % (filePageCount*interval) == 0:
                file = datailTargetDir+'items_page_%d_%d_interval%d.csv'%(p, p+(filePageCount*interval)-1, interval)
                create_csv(file, itemDetailCsvHeaders)
                # if not os.path.exists(file):
                #     create_csv(file, itemDetailCsvHeaders)
                # else:
                #     os.remove(file)
                #     create_csv(file, itemDetailCsvHeaders)

            res1 = requests.get(pageurl%p, headers=header) #商品清單頁面
            res1.encoding = 'big5'
            soup1 = BeautifulSoup(res1.text)

            #抓"優先曝光"方塊
            if len(soup1.select('.featured-first')) != 0:
                contentFeatured = soup1.select('.featured-first')[0]
                sub1sub2FeaturedTemp = contentFeatured.findAll('tr', {'class':['sub1', 'sub2']})

                #合併sub1, sub2為list中同element
                sub1sub2Featured = []
                for i in range(0, len(sub1sub2FeaturedTemp), 2):
                    soup = BeautifulSoup(sub1sub2FeaturedTemp[i].prettify()+sub1sub2FeaturedTemp[i+1].prettify())
                    sub1sub2Featured.append(soup)

                for row in sub1sub2Featured:
                    soldCount = int(row.select('.total')[0].text.strip()) #取出清單頁面的銷售量
                    if not soldCount == 0: #銷售量不為零才抓
                        link = [tag['href'] for tag in row.select('.image')[0].select('a')][0]
                        itemCode = getItemCode(link).encode('utf8') #???這邊一定要加encode???

                        append_detail_csv(link, header, file) #???如何能在後面當掉情況下不做這項???
                        print 'item %s detail saved.'%itemCode

                        recordFile = recordTargetDir + '%s.csv'%itemCode
                        getSalesRecord(itemCode, header, recordFile)

                        print 'Sales record %s saved.'%itemCode

            #抓"全部商品"方塊
            if len(soup1.select('.all-products')) != 0:
                contentAll = soup1.select('.all-products')[0]
                sub1sub2AllTemp = contentAll.findAll('tr', {'class':['sub1', 'sub2']})

                #合併sub1, sub2為list中同element
                sub1sub2All = []
                for i in range(0, len(sub1sub2AllTemp), 2):
                    soup = BeautifulSoup(sub1sub2AllTemp[i].prettify()+sub1sub2AllTemp[i+1].prettify())
                    sub1sub2All.append(soup)

                for row in sub1sub2All:
                    soldCount = int(row.select('.total')[0].text.strip()) #取出清單頁面的銷售量
                    if not soldCount == 0: #銷售量不為零才抓
                        link = [tag['href'] for tag in row.select('.image')[0].select('a')][0]
                        itemCode = getItemCode(link).encode('utf8')

                        append_detail_csv(link, header, file)
                        print 'item %s detail saved.'%itemCode

                        recordFile = recordTargetDir + '%s.csv'%itemCode
                        getSalesRecord(itemCode, header, recordFile)

                        print 'Sales record %s saved.'%itemCode

        except Exception, e:
            errorcount += 1
            print 'Error occurred when capturing page %d. error %d.'%(p, errorcount)
            logging.exception(e)
            continue
        break
    pageFinishTime = int(round(time.time() * 1000))
    period = pageFinishTime - pageStartTime
    totalEstimatedPeriod = period*(endPageNumber - p)/(1000*60*60)
    print '---------------------------------Page %d done.---------------------------------'%p
    print 'Period of this page: %dms.'%period
    time.sleep(randint(1,10)*0.1)
print 'Job done!'