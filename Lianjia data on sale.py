import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime

# from sqlalchemy import all_
# import time
# import random
# import time


# from tools import WriteToExcel, WriteToExcel_df


def make_soup(url):
    # parse a html page for analysi with bs4
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
        'Cookie': 'lianjia_uuid=e2edd406-894e-4a9d-a490-7f075aff39f7; UM_distinctid=17e32d2927117-018ec5b8f9091d-f791b31-e1000-17e32d292737f; _smt_uid=61d7c33e.4ba9cfc4; _ga=GA1.2.1838195870.1641530191; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2217e32d596505fb-0b2bb82c48bc9f-f791b31-2073600-17e32d59651499%22%2C%22%24device_id%22%3A%2217e32d596505fb-0b2bb82c48bc9f-f791b31-2073600-17e32d59651499%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _gid=GA1.2.1765217636.1645677395; _jzqc=1; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1645677407,1645690672,1645758364; select_city=110000; _jzqx=1.1645681873.1645764687.4.jzqsr=bj%2Elianjia%2Ecom|jzqct=/ershoufang/andingmen/.jzqsr=bj%2Elianjia%2Ecom|jzqct=/ershoufang/dianmen/tt2l1/; _jzqckmp=1; lianjia_ssid=32ba4ba8-7158-40f5-9672-fec1c15a61ab; _jzqa=1.2192555456837514500.1641530184.1645764687.1645770475.12; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1645770944; _jzqb=1.6.10.1645770475.1',
        'Referer':'https://bj.lianjia.com/',
        'Connection':'keep-alive'
        }
    # text = requests.get(url, headers=headers,verify=False).text
    text = requests.get(url, headers=headers,verify=True).text
    soup = bs(text, features='lxml')
    return soup

def get_page_number(url):
    # get the number of pages for a region or sub-region
    soup = make_soup(url)
    temp = soup.find_all(name='div', attrs={'class': 'page-box house-lst-page-box'})
    try:
        pages = int(re.findall('{"totalPage":(\d*),', temp[0].get('page-data'))[0])
    except:
        # there is case that there's no data for a page (like in Changping Baishan)
        pages = 1
    return pages

def url_generator_for_all(url, pages):
    # generate a list of urls for all the pages in a region/sub-region
    pageinfo = ['']
    url_list = []
    if pages > 2:
        for i in range(2, pages + 1):
            pageinfo.append('pg' + str(i) + r'/')
        for i in pageinfo:
            url_full = url + i
            url_list.append(url_full)
        return url_list
    elif pages == 1:
        url_list.append(url)
    elif pages == 2:
        url_list.append(url)
        url_list.append(url + 'pg2/')
    return url_list

def get_region_links(url_base):
    # get the list of urls for all the regions in a city, like Haidian, Chaoyang, etc.
    soup_base = make_soup(url_base)
    # get the links in the historical page by region
    links_soup = soup_base.findAll(name='div', attrs={'data-role': 'ershoufang'})
    links = [i.get('href') for i in links_soup[0].find_all('a')]
    regions = [i.text for i in links_soup[0].find_all('a')]
    links_region = [url_base + i[11:] for i in links]
    region_links = dict(zip(regions, links_region))
    return region_links

def get_subregion_links(url_base, link):
    '''
    url_base
    link = url_base + region_name
    '''
    #  for each region (like Changyang),get the list of links for its sub-regions (like Laiguangyin)
    region_soup = make_soup(link)
    try:
        links_temp = region_soup.find_all(name='div', attrs={'data-role': 'ershoufang'})[0].find_all('div')[1].find_all(
            'a')
        links_subregion_short = [i.get('href') for i in links_temp]
        links_subregion = [url_base + i[12:] for i in links_subregion_short]
        subregions = [i.text for i in links_temp]
        subregion_links = dict(zip(subregions, links_subregion))
    except:
        subregion_links = {'N/A': link}
    return subregion_links

def get_subregion_links_with_criteria(url_base, region_name, *args):
    
    '''
    Criteria include: New, One_bedroom
    for each region (like Changyang),get the list of links for its sub-regions (like Laiguangyin)
    
    '''

    Criteria ={
        'New':'tt2',
        'One_bedroom':'l1'
    }

    # Set a default criteria if there's no input
    if len(args)==0:
        args = Criteria
    else:
        args = args

    #Create the string for the criteria to be used in url

    args_in_url = [Criteria[arg] for arg in args] 

    arg_string=str()

    for arg in args_in_url:
        arg_string=arg_string + str(arg)

    # Create the link of the subregion
    link = url_base + str(region_name)
    region_soup = make_soup(link)

    try:
        links_temp = region_soup.find_all(name='div', attrs={'data-role': 'ershoufang'})[0].find_all('div')[1].find_all(
            'a')
        links_subregion_short = [i.get('href') for i in links_temp]
        links_subregion = [url_base + i[11:] for i in links_subregion_short]
        subregions = [i.text for i in links_temp]
        subregion_links = dict(zip(subregions, links_subregion))
    except:
        subregion_links = {'N/A': link}
    
    # Add criteria to the subregion links
    sub_region_links_with_criteria=dict()
    for key in subregion_links:
        sub_region_links_with_criteria[key]=subregion_links[key]+arg_string+'/'
    
    return sub_region_links_with_criteria


def get_deal_urls(sub_region_url):
    #get the list of urls for a page in the sub-region page
    sub_region_page_soup = make_soup(sub_region_url)
    url_div = sub_region_page_soup.find_all(name='div', attrs={'class': 'title'})
    urls_per_deal = []
    try:
        for i in url_div:
            if i.find_all('a') and i.find_all('a')[0].get('href') is not None:
                deal_url = i.find_all('a')[0].get('href')
                urls_per_deal.append(deal_url)
    except:
        pass
    return urls_per_deal

def get_deal_page_data_on_sale(url):
    page_soup = make_soup(url)

    try:
        price = float(page_soup.find_all(name='span', attrs={'class': 'total'})[0].text)
    except:
        price = None

    try: 
        unit_price = page_soup.find_all(name='span', attrs={'class': 'unitPriceValue'})[0].text
    except:
        unit_price=None
    try:
        around_info = page_soup.find_all(name='div', attrs={'class': 'aroundInfo'})[0]
    except:
        around_info = None
    try:    
        block_name = around_info.find_all(name='a',attrs={'target':'_blank','class':'info'})[0].text
    except:
        block_name=None
    try:
        region = around_info.find_all(name='a',attrs={'target':'_blank'})[1].text
    except:
        region=None    
    try:
        sub_region = around_info.find_all(name='a',attrs={'target':'_blank'})[2].text
    except:
        sub_region=None
    # The basic attributes of the house
    try:
        basic_attrs = page_soup.find_all(name='div', attrs={'class': 'content'})[2].find_all('li')
    except:
        basic_attrs=None 
    try:
        layout = basic_attrs[0].find("span",text='房屋户型').next_sibling
    except:
        layout=None        
    try:
        floor = basic_attrs[1].find("span",text='所在楼层').next_sibling
    except:
        floor=None        
    try:
        area = basic_attrs[2].find("span",text='建筑面积').next_sibling
    except:
        area=None        
    try:
        structure = basic_attrs[3].find("span",text='户型结构').next_sibling
    except:
        structure=None        
    try:
        area_internal = basic_attrs[4].find("span",text='套内面积').next_sibling
    except:
        area_internal=None        
    try:
        building_type = basic_attrs[5].find("span",text='建筑类型').next_sibling
    except:
        building_type=None        
    try:
        direction = basic_attrs[6].find("span",text='房屋朝向').next_sibling
    except:
        direction=None        
    try:
        building_material = basic_attrs[7].find("span",text='建筑结构').next_sibling
    except:
        building_material=None        
    try:
        decoration = basic_attrs[8].find("span",text='装修情况').next_sibling
    except:
        decoration=None        
    try:
        lifts_number = basic_attrs[9].find("span",text='梯户比例').next_sibling
    except:
        lifts_number=None        
    try:
        heating = basic_attrs[10].find("span",text='供暖方式').next_sibling
    except:
        heating=None        
    try:
        lifts = basic_attrs[11].find("span",text='配备电梯').next_sibling
    except:
        lifts=None        

    # the basic attributes of the deal
    try:
        deal_attrs = page_soup.find_all(name='div', attrs={'class': 'content'})[3].find_all('li')
    except:
        deal_attrs=None        
    try:
        online_date = deal_attrs[0].find_all('span')[1].text
    except:
        online_date=None        
    try:
        deal_attributes = deal_attrs[1].find_all('span')[1].text
    except:
        deal_attributes=None        
    try:
        last_transaction_date = deal_attrs[2].find_all('span')[1].text
    except:
        last_transaction_date=None        
    try:
        property_use = deal_attrs[3].find_all('span')[1].text
    except:
        property_use=None        
    try:
        property_age = deal_attrs[4].find_all('span')[1].text
    except:
        property_age=None        
    try:
        property_owner = deal_attrs[5].find_all('span')[1].text
    except:
        property_owner=None        
    try:
        morgage_status = deal_attrs[6].find_all('span')[1].text
    except:
        morgage_status=None        
    try:
        certificate_review =deal_attrs[7].find_all('span')[1].text
    except:
        certificate_review=None        

    #additional info
    try:
        tag = page_soup.find_all(name='div', attrs={'class': 'content'})[4].text.strip()
    except:
        tag=None        
    try:
        highlight =page_soup.find_all(name='div', attrs={'class': 'content'})[5].text.strip()
    except:
        highlight=None
    try:
        additional_description = page_soup.find_all(name='div', attrs={'class': 'content'})[6].text.strip()
    except:
        additional_description=None        
    try:
        environment = page_soup.find_all(name='div', attrs={'class': 'content'})[7].text.strip()
    except:
        environment=None        
    try:
        tax_summary = page_soup.find_all(name='div', attrs={'class': 'content'})[8].text.strip()
    except:
        tax_summary=None        
    try:
        transportation = page_soup.find_all(name='div', attrs={'class': 'content'})[9].text.strip()
    except:
        transportation=None        
    try:
        unit_price_in_w = float(unit_price[:-4])
    except:
        unit_price_in_w=None


    #summary
    deal_info = {}

    deal_info['房屋价格']=price
    deal_info['房屋单价']=unit_price
    deal_info['单价万元'] = unit_price_in_w
    deal_info['小区名称']=block_name
    deal_info['所在区域']= region
    deal_info['小区位置']= sub_region
    deal_info['房屋户型']= layout
    deal_info['所在楼层']=floor
    deal_info['建筑面积']=area
    deal_info['户型结构']=structure
    deal_info['套内面积']=area_internal
    deal_info['建筑类型']=building_type
    deal_info['房屋朝向']=direction
    deal_info['建筑结构']=building_material
    deal_info['装修情况']=decoration
    deal_info['梯户比例']=lifts_number
    deal_info['供暖方式']=heating
    deal_info['配备电梯']=lifts
    deal_info['挂牌时间']=online_date
    deal_info['交易权属']=deal_attributes
    deal_info['上次交易']=last_transaction_date
    deal_info['房屋用途']=property_use
    deal_info['房屋年限']=property_age
    deal_info['产权所属']= property_owner
    deal_info['抵押信息']=morgage_status
    deal_info['房本备件']=certificate_review
    deal_info['房源标签']=tag
    deal_info['户型介绍']=additional_description
    deal_info['核心卖点']=highlight
    deal_info['周边配套']=environment
    deal_info['税费解析']=tax_summary
    deal_info['交通出行']=transportation
    deal_info['房源链接']= url

    df=pd.DataFrame(list(deal_info.items())).T
    df.columns=df.iloc[0]
    df=df.iloc[1:,:]

    #remove duplicates
    df.drop_duplicates(subset='房源链接',keep='first',inplace=True)

    return  df

def get_regional_data(url_base,region_name):

    sub_region_links = get_subregion_links(url_base, url_base+region_name)
    
    data=pd.DataFrame()
    # all_urls = []
    # sub_region_page_links=[]
    

    for key in sub_region_links:
        # temp_list = url_generator_for_all(sub_region_links[key],get_page_number(sub_region_links[key]))
        # sub_region_page_links.extend(temp_list)
        sub_region_page_links = url_generator_for_all(sub_region_links[key],get_page_number(sub_region_links[key]))
        for link in sub_region_page_links:
            print("Getting data from link: "+ link)
            urls_in_a_page = get_deal_urls(link)
            for url in urls_in_a_page:
                deal_data= get_deal_page_data_on_sale(url)
                data = pd.concat([data,deal_data])

    #remove the duplicates       
    # all_urls = list(set(all_urls))

    # for url in all_urls:
        # deal_data = get_deal_page_data_on_sale(url)
        # data =pd.concat([data,deal_data])
    data.drop_duplicates(subset='房源链接',keep='first',inplace=True)
    
    return data

def get_regional_data_with_criteria(url_base,region_name,*args):
    '''
    Region_name: string of the region, such as 'dongcheng'

    '''

    sub_region_links = get_subregion_links_with_criteria(url_base, region_name,*args)
    
    data=pd.DataFrame()

    for key in sub_region_links:
        sub_region_page_links = url_generator_for_all(sub_region_links[key],get_page_number(sub_region_links[key]))
        for link in sub_region_page_links:
            urls_in_a_page = get_deal_urls(link)
            for url in urls_in_a_page:
                print('Getting data from '+url)
                deal_data = get_deal_page_data_on_sale(url)
                data =pd.concat([data,deal_data])
    return data


def get_data_for_recent_one_bedroom():
    url = 'https://bj.lianjia.com/ershoufang/tt2l1/' 
    page = get_page_number(url)
    data = pd.DataFrame()
    page_links = url_generator_for_all(url,page)
    
    for link in page_links:
        urls_in_a_page = get_deal_urls(link)
        for url in urls_in_a_page:
            deal_data = get_deal_page_data_on_sale(url)
            data= pd.concat([data,deal_data])
    return data


def main():

    url_base_Beijing_on_sale = r'https://bj.lianjia.com/ershoufang/'
    
    region_of_interest = {
        # "延庆":"yanqing",
        # "密云":"miyun",
        # "怀柔":"huairou",
        # "平谷":"pinggu",
        # "昌平":"changping",
        # "顺义":"shunyi",
        
        
        "石景山":"shijingshan",
        "通州":"tongzhou",
        "大兴":"daxing",
        "亦庄":"yizhuangkaifaqu",
        "房山":"fangshan",
        "门头沟":"mentougou",
        "东城":"dongcheng",
        "西城":"xicheng",
        "海淀":"haidian",
        "丰台":"fengtai",
        "朝阳":"chaoyang"

    }

    all_beijing_data = pd.DataFrame()

    for key in region_of_interest:
        regional_data = get_regional_data(url_base_Beijing_on_sale,region_of_interest[key])
        # regional_data = get_regional_data_with_criteria(url_base_Beijing_on_sale,region_of_interest[key],'New','One_bedroom')
        regional_data.to_excel('Lianjia housing market data for '+key+'.xlsx')
        all_beijing_data=pd.concat([all_beijing_data,regional_data])
    
    
    all_beijing_data.to_excel('Lianjia all Beijing housing market data.xlsx')
   
   
   
   
    # data = get_data_for_recent_one_bedroom()
    # data.to_excel('Lianjia recent data for one bedroom.xlsx')




if __name__ == '__main__':
    main()
