import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
from tools import WriteToExcel, WriteToExcel_df



def GetPages(url):
    headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    cookies ={'Cookie': 'BAIDUID=A467EBC2C2D0C1F5CE71C86F2D851B89:FG=1; PSTM=1569895226; BIDUPSID=9BD73512109ADEBC79D0E6031A361FF2; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid_BFESS=3401447befc2a1f1fb58e1332e7a70a45049; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598'}
    text = requests.get(url, headers=headers, cookies = cookies).text
    soup = bs(text, features='lxml')
    list_of_info = soup.findAll(name='ul', attrs={'class':'listContent'})
    
    # pages = re.findall('<a href="/ershoufang/pg2c1111027382441rs国际城" data-page="2">2</a>')
    title_all = list_of_info[0].findAll(name='div',attrs={'class':'title'})
    houseinfo = list_of_info[0].findAll(name='div',attrs={'class':'houseInfo'})
    dealdate = list_of_info[0].findAll(name='div',attrs={'class':'dealDate'})
    totalprice = list_of_info[0].findAll(name='div',attrs={'class':'totalPrice'})
    positioninfo = list_of_info[0].findAll(name='div',attrs={'class':'positionInfo'})
    unitprice = list_of_info[0].findAll(name='div',attrs={'class':'unitPrice'})
    dealhouseinfo = list_of_info[0].findAll(name='div',attrs={'class':'dealHouseInfo'})
    dealquote = list_of_info[0].findAll(name='div',attrs={'class':'dealCycleeInfo'})
    
    block = [i.text.split(' ')[0] for i in title_all]
    rooms = [i.text.split(' ')[1] for i in title_all]
    area = []
    for i in title_all:
        if len(i.text.split(' '))==3:
            area.append(float(i.text.split(' ')[2][:-2]))
        else:
            area.append(10)
    direction = [i.text.split('|')[0] for i in houseinfo]
    decoration = [i.text.split('|')[1] for i in houseinfo]
    date =[]
    for i in dealdate:
        if len(i.text.split('.'))==2:
            date.append(datetime.strptime(i.text,'%Y.%m'))
        else:
            date.append(datetime.strptime(i.text,'%Y.%m.%d'))
    year = [i.year for i in date]
    month = [i.month for i in date]
    price = [i.text[:-1] for i in totalprice]
    AveragePrice = []
    for i in price:
        if '-' in i:
            a = float(i.split('-')[0])
            b = float(i.split('-')[1])
            AveragePrice.append((a+b)/2)
        else:
            AveragePrice.append(float(i))
    position = [i.text for i in positioninfo]
    price_per_m2 = [i.text[:-3] for i in unitprice]
    average_unit_price=[]
    for i in price_per_m2:
        try:
            if '-' in i:
                a = float(i.split('-')[0])
                b = float(i.split('-')[1])
                average_unit_price.append((a+b)/2)
            else:
                average_unit_price.append(float(i))
        except:
            average_unit_price.append('N/A')
        
    House_info = [i.text for i in dealhouseinfo]
    deal_info = [i.text for i in dealquote]
    quote = [re.findall('牌(\d*)', i.text) for i in dealquote]
    cycletime = [re.findall('期(\d*)', i.text) for i in dealquote]
    
    data = pd.DataFrame({'block':block, 
                         'rooms':rooms,
                         'area':area,
                         'direction':direction,
                         'decoration':decoration,
                         'deal date':date,
                         'year':year,
                         'month':month,
                         'deal price range':price,
                         'deal price':AveragePrice,
                         'position':position,
                         'unit price range':price_per_m2,
                         'unit price':average_unit_price
                         # 'house info':House_info,
                         # 'deal info':deal_info,
                         # 'quotation':quote,
                         # 'cycle time':cycletime
                         })
    
    return data

    
def PriceInfo(url,headers, cookies):
    text = requests.get(url, headers=headers, cookies = cookies).text
    soup = bs(text)
    rooms =[i.text.strip().split('|')[0] for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    area = [float(i.text.strip().split('|')[1][:-3]) for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    direction = [i.text.strip().split('|')[2] for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    decoration = [i.text.strip().split('|')[3] for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    floor = [i.text.strip().split('|')[4] for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    year = [int(i.text.strip().split('|')[5][:-3].strip()) for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    buildingtype = [i.text.strip().split('|')[6] for i in soup.findAll(name='div', attrs={'class':'houseInfo'})]
    price = [float(i.text[:-1]) for i in soup.findAll(name = 'div', attrs={'class':'totalPrice'})]
    block =[i.text.strip() for i in soup.findAll(name='a', attrs={'data-el':'region'})]
    return pd.DataFrame({'block':block,'rooms':rooms, 'area':area, 'price':price, 'direction':direction,'decoration':decoration,'floor':floor, 'year':year, 'building type':buildingtype})

def UrlGenerator(block, pages):
    
    pageinfo =['']
    url_list=[]
    for i in range(1,pages+1):
        pageinfo.append('pg'+str(i))
    
    url_part1 = r'https://bj.lianjia.com/chengjiao/'
    if block == 'gjc':
        for i in pageinfo:
            url = url_part1+i+r'c1111027382441/?sug=%E4%B8%AD%E5%9B%BD%E9%93%81%E5%BB%BA%E5%9B%BD%E9%99%85%E5%9F%8E'
            url_list.append(url)
    elif block == 'rzgg':
        for i in pageinfo:
            url = url_part1+i+r'c1111045303586/?sug=润泽公馆'
            url_list.append(url)        
    elif block == 'hmc':
        for i in pageinfo:
            url = url_part1+i+r'c1111027375158rs华贸城/'
            url_list.append(url) 
    elif block == 'shbj':
        for i in pageinfo:
            url = url_part1+i+r'c1111041153546/?sug=世华泊郡'
            url_list.append(url)
    elif block == 'fxdd':
            url = url_part1+i+r'c1111027379985/?sug=天润福熙大道'
            url_list.append(url)        
    return url_list


def main():
    # url = r'https://bj.lianjia.com/ershoufang/c1111027382441rs%E5%9B%BD%E9%99%85%E5%9F%8E/'
    url_for_sale= r'https://bj.lianjia.com/ershoufang/c1111027382441/?sug=%E4%B8%AD%E5%9B%BD%E9%93%81%E5%BB%BA%E5%9B%BD%E9%99%85%E5%9F%8E'
    url_historical = r'https://bj.lianjia.com/chengjiao/c1111027382441/?sug=%E4%B8%AD%E5%9B%BD%E9%93%81%E5%BB%BA%E5%9B%BD%E9%99%85%E5%9F%8E'
    pages_gjc = 13
    pages_rzgg =11
    pages_shbj =14
    pages_hmc = 50
    
    blocks ={
        'gjc':13,
        'rzgg':11,
        'shbj':14,
        'hmc':50,
        'fxdd':9
        }
    
    # url_historical_list=[]
    # url_historical_list.append(url_historical)
    # for i in range(2,pages+1):
    #     url = r'https://bj.lianjia.com/chengjiao/'+'pg'+str(i)+r'c1111027382441/?sug=%E4%B8%AD%E5%9B%BD%E9%93%81%E5%BB%BA%E5%9B%BD%E9%99%85%E5%9F%8E'
    #     url_historical_list.append(url)
    # data_list = []
    data =pd.DataFrame()
    for block in blocks:
        for i in UrlGenerator(block,blocks[block]):
            pagedata = GetPages(i)
            data = pd.concat([data,pagedata])
            # data_list.append(data)
    
    
    filename = 'lianjia historical data'+' '+ time.ctime().replace(':','_')+'.xlsx'
    with pd.ExcelWriter(filename) as writer:
        data.to_excel(writer, sheet_name = datetime.today().strftime('%Y-%m-%d'))
    
    # data_rzgg =pd.DataFrame()
    
    # for i in UrlGenerator('gjc',pages_gjc):
    #     pagedata = GetPages(i)
    #     data_gjc = pd.concat([data_gjc,pagedata])
    
    # data_list.append(data_gjc)    
    
    
    # WriteToExcel('lianjia','lianjia', data)    

    # Price = PriceInfo(url,headers,cookies)
    # with pd.ExcelWriter('Lianjia historical info.xlsx') as Writer:
    #     data.to_excel(Writer, sheet_name = 'Lianjia')



if __name__ == '__main__':
    main()
