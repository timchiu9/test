import requests, time, re, os
from bs4 import BeautifulSoup
from random import randint

url='http://class.ruten.com.tw/category/sub00.php?c=00120007'
pageurl= url+'&p=1&p=%d'

payload = {}
header = {
'Cookie':'ruten_ad_20150108-122732_expire=Tue%2C%2003%20Feb%202015%2006%3A39%3A18%20GMT; ruten_ad_20150108-122732=1; ruten_ad_20150130-164849_expire=Tue%2C%2003%20Feb%202015%2006%3A39%3A48%20GMT; ruten_ad_20150130-164849=1; _ts_id=3D04360E3C083E0D3D; _gat=1; _ga=GA1.3.1515021042.1422859158',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'}

res = requests.get(url,headers=header)
res.encoding=('big5')
soup = BeautifulSoup(res.text)
page = int(soup.select('.page-total')[0].text)
print 'This category has %d pages.'%page

startPageNumber = 6401
endPageNumber = page
date = '0211'
dir = "ruten/%s/"%date
if not os.path.exists(dir):
    os.makedirs(dir)
ruten_file = open(dir + "ruten_list_%d.txt"%startPageNumber, 'w')

for p in range(startPageNumber, endPageNumber+1, 1):
    errorcount = 0
    while True:
        try:
            if (p-1)%100==0:
                ruten_file.close()
                ruten_file = open(dir + "ruten_list_%d.txt"%p, 'w')
            res1 = requests.get(pageurl%p,headers=header)
            res1.encoding=('big5')
            #print res1.text
            soup1 = BeautifulSoup(res1.text)
            # contentFeatured = soup1.select('.featured-first')[0]

            if len(soup1.select('.featured-first')) != 0:
                contentFeatured = soup1.select('.featured-first')[0]
                # print contentFeatured
                sub1Featured = contentFeatured.findAll('tr', {'class':'sub1'})
                # print sub1Featured
                for row in sub1Featured:
                    link = [tag['href'] for tag in row.select('.image')[0].select('a')][0]
                    ruten_file.write(link + "\n")

            if len(soup1.select('.all-products')) != 0:
                contentAll = soup1.select('.all-products')[0]
                # print contentAll
                sub1All = contentAll.findAll('tr', {'class':'sub1'})
                # print sub1All
                for row in sub1All:
                    link = [tag['href'] for tag in row.select('.image')[0].select('a')][0]
                    ruten_file.write(link + "\n")

        except Exception as detail:
            errorcount += 1
            print 'Error occurred when capturing page %d. error %d.'%(p, errorcount)
            print detail
            continue
        break
    print 'page %d done.'%p
    time.sleep(randint(1,10)*0.1)
ruten_file.close()
print 'Job done!'