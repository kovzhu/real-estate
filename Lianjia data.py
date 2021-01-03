import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
from tools import WriteToExcel, WriteToExcel_df


def make_soup(url):
    #parse a html page for analysi with bs4
    headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    cookies ={'Cookie': 'BAIDUID=A467EBC2C2D0C1F5CE71C86F2D851B89:FG=1; PSTM=1569895226; BIDUPSID=9BD73512109ADEBC79D0E6031A361FF2; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid_BFESS=3401447befc2a1f1fb58e1332e7a70a45049; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598'}
    text = requests.get(url, headers=headers, cookies = cookies).text
    soup = bs(text, features='lxml')
    return soup

def get_page_number(url):
    #get the number of pages for a region or sub-region
    soup= make_soup(url)
    temp=soup.find_all(name='div', attrs={'class':'page-box house-lst-page-box'})
    try:
        pages = int(re.findall('{"totalPage":(\d*),',temp[0].get('page-data'))[0])
    except:
    # there is case that there's no data for a page (like in Changping Baishan)
        pages = 1
    return pages
    
def GetPages(url):
    # get all the data in a page and store it in a dataframe (data), and return the data
    soup = make_soup(url)
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
    # rooms = [i.text.split(' ')[1] for i in title_all]
    rooms = []
    for i in title_all:
        try:
            rooms.append(i.text.split(' ')[1])
        except:
            rooms.append('N/A')
    
    area = []
    for i in title_all:
        try:    
            if len(i.text.split(' '))==3:
                    area.append(float(i.text.split(' ')[2][:-2]))
            else:
                area.append(10)
        except:
            area.append('N/A')
    direction = [i.text.split('|')[0] for i in houseinfo]
    decoration = [i.text.split('|')[1] for i in houseinfo]
    date =[]
    for i in dealdate:
        try:
            if len(i.text.split('.'))==2:
                date.append(datetime.strptime(i.text,'%Y.%m'))
            else:
                date.append(datetime.strptime(i.text,'%Y.%m.%d'))
        except:
            date.append('N/A')
    year = [i.year for i in date]
    month = [i.month for i in date]
    price = [i.text[:-1] for i in totalprice]
    AveragePrice = []
    for i in price:
        try:
            if '-' in i:
                a = float(i.split('-')[0])
                b = float(i.split('-')[1])
                AveragePrice.append((a+b)/2)
            else:
                AveragePrice.append(float(i))
        except:
            AveragePrice.append('N/A')
            
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
        
    # House_info = [i.text for i in dealhouseinfo]
    # deal_info = [i.text for i in dealquote]
    # quote = [re.findall('牌(\d*)', i.text) for i in dealquote]
    # cycletime = [re.findall('期(\d*)', i.text) for i in dealquote]
    
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

def url_generator_for_all(url, pages):
    #generate a list of urls for all the pages in a region/sub-region
    pageinfo = ['']
    url_list = []
    if pages>2:
        for i in range(2,pages+1):
            pageinfo.append('pg'+str(i)+r'/')
        for i in pageinfo:
            url_full = url + i
            url_list.append(url_full)
        return url_list
    elif pages == 1:
        url_list.append(url)
    elif pages ==2:
        url_list.append(url)
        url_list.append(url+'pg2/')
    return url_list
        

def get_region_links(url_base):
    #get the list of urls for all the regions in a city, like Haidian, Chaoyang, etc.
    soup_base = make_soup(url_base)
    #get the links in the historical page by region
    links_soup = soup_base.findAll(name ='div',attrs={'data-role':'ershoufang'})
    links = [i.get('href') for i in links_soup[0].find_all('a')]
    regions = [i.text for i in links_soup[0].find_all('a')]
    links_region = [url_base+i[11:] for i in links]
    region_links = dict(zip(regions, links_region))
    return region_links   

def get_subregion_links(url_base,link):
    #for each region (like Changyang),get the list of links for its sub-regions (like Laiguangyin)
    region_soup = make_soup(link)
    links_temp = region_soup.find_all(name ='div', attrs={'data-role':'ershoufang'})[0].find_all('div')[1].find_all('a')
    links_subregion_short = [i.get('href') for i in links_temp]
    links_subregion = [url_base+i[11:] for i in links_subregion_short]
    subregions = [i.text for i in links_temp]
    subregion_links = dict(zip(subregions,links_subregion))
    return subregion_links    

def get_regional_data(url_base,region, link):
    #get all the data in a region, by looping its subregions
    data=pd.DataFrame()
    subregion_links = get_subregion_links(url_base,link)
    
    # loop for every sub-region in each region
    for sub_region in subregion_links:
        pages = get_page_number(subregion_links[sub_region])
        all_urls = url_generator_for_all(subregion_links[sub_region],pages)
        for i in all_urls:
            pagedata = GetPages(i)
            try:
                pagedata.loc[:,'region']=region
                pagedata.loc[:,'sub-region']=sub_region
            except:
                pass
            data = pd.concat([data, pagedata]) 
    # filename = 'lianjia historical data '+city+' '+region +' '+ datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xlsx'
    # with pd.ExcelWriter(filename) as writer:
    #     data.to_excel(writer, sheet_name = region)    
    
    return data

    
def get_all_data(url_base):
    #Get all regional data as dataframes, and store all the dfs in a list
    region_links =get_region_links(url_base)
    data_by_region = []
    for region in region_links:
        regional_data = get_regional_data(url_base,region,region_links[region])
        data_by_region.append(regional_data)
    return data_by_region

def city_name(url):
    city_code = re.findall('https://(\w*).',url)[0]
    if city_code == 'bj':
        city='北京'
    elif city_code == 'sh':
        city ='上海'
    elif city_code == 'cd':
        city ='成都'
    elif city_code == 'sz':
        city = '深圳'
    else:
        city = 'unknown'
    return city
    
def main():
    url_base_beijing =r'https://bj.lianjia.com/chengjiao/'
    url_base_shanghai =r'https://sh.lianjia.com/chengjiao/'
    url_base_chengdu =r'https://cd.lianjia.com/chengjiao/'
    url_base_shenzhen =r'https://sz.lianjia.com/chengjiao/'
    
    city = city_name(url_base_beijing) 
    
    #Get data by region and store it in excel
    links = get_region_links(url_base_beijing)
    region = '昌平'
    # beijng valid regions:
    #     东城
    #     西城
    #     朝阳
    #     海淀
    #     丰台
    #     石景山
    #     通州
    #     昌平
    #     大兴
    #     亦庄开发区
    #     顺义
    #     房山
    #     门头沟
    #     平谷
    #     怀柔
    #     密云
    #     延庆
    data = get_regional_data(url_base_beijing,region,links[region])
    filename = 'lianjia historical data '+city+' '+region +' '+ datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xlsx'
    with pd.ExcelWriter(filename) as writer:
        data.to_excel(writer, sheet_name = datetime.today().strftime('%Y-%m-%d'))    

    #get all data in a city and store them in excel
    # datalist = get_all_data(url_base_beijing)
    
    # filename = 'lianjia historical data '+city+ datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.xlsx'
    # with pd.ExcelWriter(filename) as writer:
    #     # writer.book = load_workbook(filename)
    #     for i in range(0,len(datalist)):
    #         datalist[i].to_excel(writer, sheet_name = 'sheet'+str(i))
    

if __name__ == '__main__':
    main()
