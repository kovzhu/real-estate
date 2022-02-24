import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from datetime import datetime
# import time
# import random
# import time


# from tools import WriteToExcel, WriteToExcel_df


def make_soup(url):
    # parse a html page for analysi with bs4
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
    cookies = {
        'Cookie': 'BAIDUID=A467EBC2C2D0C1F5CE71C86F2D851B89:FG=1; PSTM=1569895226; BIDUPSID=9BD73512109ADEBC79D0E6031A361FF2; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid=3401447befc2a1f1fb58e1332e7a70a45049; ab_jid_BFESS=3401447befc2a1f1fb58e1332e7a70a45049; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598'}
    text = requests.get(url, headers=headers, cookies=cookies, verify=False).text
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
    # for each region (like Changyang),get the list of links for its sub-regions (like Laiguangyin)
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
    return subregion_links

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
        price = page_soup.find_all(name='span', attrs={'class': 'total'})[0].text

    try: 
        unit_price = page_soup.find_all(name='span', attrs={'class': 'unitPriceValue'})[0].text
    except:
        unit_price=None
    try:
        around_info = page_soup.find_all(name='div', attrs={'class': 'aroundInfo'})[0]
    except:
        around_info = page_soup.find_all(name='div', attrs={'class': 'aroundInfo'})[0]
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
        floor=None        
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

    #summary
    deal_info = {}

    deal_info['房屋价格']=price
    deal_info['房屋单价']=unit_price
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

    

    return  pd.DataFrame(list(deal_info.items())).T

def get_regional_data(url_base,region_name):

    sub_region_links = get_subregion_links(url_base, url_base+region_name)
    
    data=pd.DataFrame()

    for key in sub_region_links:
        sub_region_page_links = url_generator_for_all(sub_region_links[key],get_page_number(sub_region_links[key]))
        for link in sub_region_page_links:
            urls_in_a_page = get_deal_urls(link)
            for url in urls_in_a_page:
                deal_data = get_deal_page_data_on_sale(url)
                pd.concat([data,deal_data])
    return data

def main():

    url_base_Beijing_on_sale = r'https://bj.lianjia.com/ershoufang/'
    region_of_interest = {
        "朝阳":"chaoyang",
        "丰台":"fengtai",
        "石景山":"shijingshan",
        "通州":"tongzhou",
        "大兴":"daxing",
        "亦庄":"yizhuangkaifaqu",
        "房山":"fangshan",
        "门头沟":"mentougou",
        "东城":"dongcheng",
        "西城":"xicheng",
        "海淀":"haidian"

    }

    for key in region_of_interest:
        regional_data = get_regional_data(url_base_Beijing_on_sale,region_of_interest[key])
        regional_data.to_excel('Lianjia housing market data for'+key+'.xlsx')



    # sub_region_links = get_subregion_links(url_base_Beijing_on_sale, url_base_Beijing_on_sale+'dongcheng')
    
    # data=pd.DataFrame()

    # for key in sub_region_links:
    #     sub_region_page_links = url_generator_for_all(sub_region_links[key],get_page_number(sub_region_links[key]))
    #     for link in sub_region_page_links:
    #         urls_in_a_page = get_deal_urls(link)
    #         for url in urls_in_a_page:
    #             deal_data = get_deal_page_data_on_sale(url)
    #             pd.concat([data,deal_data])
    
    # data.to_excel('lianjia deals in dongcheng.xlsx')



if __name__ == '__main__':
    main()
