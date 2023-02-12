# file_name : NaverMapCrawling.py
# file_path : D:\bigdata10\99. 팀프로젝트\데이터셋\data_crawling_func/NaverMapCrawling.py

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import re
import time
import datetime
import math

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip

from selenium import webdriver
from bs4 import BeautifulSoup
import tqdm
from selenium.common import exceptions

import os
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")

global count_success
global count_over_fifty
global count_search_zero
global count_avoid_capcha

count_success = 0
count_over_fifty = 0
count_search_zero = 0
count_avoid_capcha = 0

global tmp_naver_search_all  # 검색결과 저장 DF 전역변수 사용
global tmp_naver_search_rejected  # 검색거부 저장 DF 전역변수 사용
tmp_naver_search_all = DataFrame(columns=['업소ID'
                                    , '업소명'
                                    , '소재지전화번호'
                                    , '소재지도로명' 
                                    , '카테고리'
                                    , '검색인덱스'
                                    , '검색주소타입'
                                    , '검색어'
                                    , '검색건수'
                                    , '수집일'
                                    ])


tmp_naver_search_rejected = DataFrame(columns=['지역'
                                        , '업소명'
                                        , '검색주소'
                                        , '검색주소타입'
                                        , '검색어'
                                        , '검색건수' 
                                        , '원인'
                                        , '수집일'
                                         ])


def send_to_input_box(keyword, input_box, fix_display_search, driver, search_button_xpath):
    # 입력박스에 검색어 입력
    print('검색어 :', keyword)
    input_box.clear()
    input_box.send_keys(keyword)
    
    
    # '현 지도에서 장소검색' 체크가 되어있지 않다면 체크
    if not fix_display_search.is_selected():
        fix_display_search.click()
    
    time.sleep(np.random.rand())
    
    # 검색 버튼 클릭
    driver.find_element_by_xpath(search_button_xpath).click()
    driver.implicitly_wait(5)
    
    # 현재 페이지 소스 가져와 parsing하기
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def crawl_naver_map_v4(series, driver):

    print('try row-num :', series.name)
    
    global tmp_naver_search_all  # 검색결과 저장 DF 전역변수 사용
    global tmp_naver_search_rejected  # 검색거부 저장 DF 전역변수 사용
    
    global count_success
    global count_over_fifty
    global count_search_zero
    global count_avoid_capcha
    
    # 입력박스 찾아서 주소 입력
    input_box = driver.find_element_by_id('search-input')
    input_box.clear()
    search_addr=''
    search_addr_type=0
    if type(series['소재지도로명']) == str:
        search_addr = series['소재지도로명']
        search_addr_type = 1
    else:
        search_addr = series['소재지지번']
        search_addr_type = 2
    
    input_box.send_keys(search_addr)
    
    # '현 지도에서 장소검색' 체크되어있다면 체크 해제
    # '(현 지도에서 장소검색' 체크박스 id : searchCurr)
    fix_display_search = driver.find_element_by_id('searchCurr')
    if fix_display_search.is_selected():
        fix_display_search.click()
    
    time.sleep(np.random.rand())
    
    # 검색 버튼 클릭
    search_button_xpath = """//*[@id="header"]/div[1]/fieldset/button"""
    driver.find_element_by_xpath(search_button_xpath).click()
    driver.implicitly_wait(5)
    
    # 입력박스에 검색어 입력
    keyword = '%s' % series['업소명'] + ' 미용실'
    soup = send_to_input_box(keyword, input_box, fix_display_search, driver, search_button_xpath)
    
    # 검색결과 건수 가져오기
    # 총 페이지수 계산하기
    if soup.find('span', 'n'):
        # 검색결과 건수
        total_result = int(soup.find('span', 'n').find('em').text.replace(',',''))
        if total_result <= 50:
            print('검색결과 %s건' % total_result)
            # 페이지 수
            total_page = math.ceil(total_result / 10)
        else:
            print('검색결과 %s건' % total_result)
            print('[%s] 검색결과 50건 초과 !!' % datetime.datetime.now())
            
            keyword = '"%s"' % series['업소명'] + ' 미용실'
            
            print('재시도 -', end=' ')
            soup = send_to_input_box(keyword, input_box, fix_display_search, driver, search_button_xpath)
           
            if soup.find('span', 'n'):
                # 검색결과 건수
                total_result = int(soup.find('span', 'n').find('em').text.replace(',',''))
                if total_result <= 50:
                    print('검색결과 %s건' % total_result)
                    # 페이지 수
                    total_page = math.ceil(total_result / 10)
                else:
                    print('검색결과 %s건' % total_result)
                    print('[%s] 검색결과 50건 초과 !!' % datetime.datetime.now())
            
                    tmp_naver_search_rejected = tmp_naver_search_rejected.append(DataFrame({
                          '지역' : series['지역']
                        , '업소명' : series['업소명']
                        , '검색주소' : search_addr
                        , '검색주소타입' : search_addr_type
                        , '검색어' : keyword
                        , '검색건수' : total_result
                        , '원인' : '검색건수 50건 초과'
                        , '수집일' : series['수집일']
                        }
                        , index=[series.name]
                        
                    ), sort=False
                    )     
                    # 오늘 날짜 출력
                    today = datetime.datetime.now().strftime('%Y-%m-%d')

                    # 검색결과가 없어 검색 실패한 데이터 csv 파일로 저장
                    tmp_naver_search_rejected.to_csv(
                          './tmp_naver_map_seoul_salon_outout_rejected_data_%s.csv' % today
                        , sep=','
                        , encoding='utf-8'
                    )
                    
                    count_over_fifty+=1
                    print(f'성공 : {count_success} | 0건 검색 : {count_search_zero} | 50건이상 검색 : {count_over_fifty} | 캡챠 우회 : {count_avoid_capcha} | 서비스 오류 : {count_service_error}\n')
                    
                    return
      
    else:
        print('검색결과 0건')
        print('[%s] 검색결과 없음 !!' % datetime.datetime.now())    

        tmp_naver_search_rejected = tmp_naver_search_rejected.append(DataFrame({
              '지역' : series['지역']
            , '업소명' : series['업소명']
            , '검색주소' : search_addr
            , '검색주소타입' : search_addr_type
            , '검색어' : keyword
            , '검색건수' : 0
            , '원인' : '검색결과 없음'
            , '수집일' : series['수집일']
            }
            , index=[series.name]

        ), sort=False
        )     

        # 오늘 날짜 출력
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        # 검색결과가 없어 검색 실패한 데이터 csv 파일로 저장
        tmp_naver_search_rejected.to_csv(
              './tmp_naver_map_seoul_salon_output_rejected_data_%s.csv' % today
            , sep=','
            , encoding='utf-8'
        )

        count_search_zero+=1
        print(f'성공 : {count_success} | 0건 검색 : {count_search_zero} | 50건이상 검색 : {count_over_fifty} | 캡챠 우회 : {count_avoid_capcha} | 서비스 오류 : {count_service_error}\n')

        return
    
    # 결과 정보 담겨있는 html 찾기
    shop_list = soup.find_all('dl', 'lsnx_det')
    
    title_list=[]
    addrRoad_list=[]
    tel_list=[]
    category_list=[]
    
    # 다음버튼 xpath : //*[@id="panel"]/div[2]/div[1]/div[2]/div[2]/div/div/a[1]
    next_page_xpath = '//*[@id="panel"]/div[2]/div[1]/div[2]/div[2]/div/div/a'
    
    fail_count=0
    id_list=[]
    for count_page in range(1, total_page+1):
        
        while 1:
            try:
                time.sleep(np.random.rand()+1)
                html = driver.page_source
                time.sleep(0.3)
                soup = BeautifulSoup(html, 'html.parser')

                info_block = soup.find('ul', 'lst_site')
                info_list = info_block.find_all('li')
                info_list = list(filter(lambda x: x.get_attribute_list('data-id')[0], info_list))
                id_list = id_list + list(map(lambda x: x.get_attribute_list('data-id')[0], info_list))
                shop_list = soup.find_all('dl', 'lsnx_det')
                break

            except AttributeError:
                fail_count+=1
                if fail_count == 3:
                    print('연결 3회 실패')
                    raise EOFError
                print('page_source 불러오기 실패. 재시도')
                continue
        
        for shop in shop_list:
            
            # 업소명 추가
            title_list.append(shop.find('a').text.strip())
            
            # 주소(도로명) 추가
            tmp_addr = shop.find('dd', 'addr').text.strip()
            addrRoad_list.append(re.sub('\s{3,}.+', '', tmp_addr))
            
            # 전화번호 추가
            try:
                tel_list.append(shop.find('dd', 'tel').text.strip())
            except:
                tel_list.append(np.nan)
            
            # 카테고리 추가
            category_list.append(shop.find('dd', 'cate').text)

        if count_page == total_page:
            break
        else:
            xpath_num = count_page%5 if count_page%5 != 0 else 5
            driver.find_element_by_xpath(next_page_xpath + '[%s]' % (xpath_num)).click()
            time.sleep(0.5)

    # 오늘 날짜 출력
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 네이버 검색결과 DataFrame에 추가(저장)
    tmp_naver_search_all = tmp_naver_search_all.append(pd.DataFrame({
              '업소ID' : id_list
            , '업소명' : title_list
            , '소재지전화번호' : tel_list
            , '소재지도로명' : addrRoad_list
            , '카테고리' : category_list
            , '검색주소타입' : search_addr_type
            , '검색인덱스' : series.name
            , '검색어' : keyword
            , '검색건수' : total_result
            , '수집일' : today
            }
        )
        , ignore_index=True
        , sort=False
    )

    # 현재까지의 네이버 검색 결과를 csv 파일로 저장
    tmp_naver_search_all.to_csv(
          './tmp_naver_map_seoul_salon_output_data_%s.csv' % today
        , sep=','
        , encoding='utf-8'
    )
    
    count_success+=1
    print('[%s] 검색 및 저장 성공 !!' % datetime.datetime.now())
    print(f'성공 : {count_success} | 0건 검색 : {count_search_zero} | 50건이상 검색 : {count_over_fifty} | 캡챠 우회 : {count_avoid_capcha} | 서비스 오류 : {count_service_error}\n')

    return

def clipboard_input(user_xpath, user_input):

        pyperclip.copy(user_input)
        driver.find_element_by_xpath(user_xpath).click()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        time.sleep(np.random.rand()+1)

def run_naver_map_search(dataframe, start, end, restart=0):

    naver_id = input('Naver ID : ')
    naver_pw = getpass('Naver PW : ')
    
    login = {
          "id" : naver_id
        , "pw" : naver_pw
    }
    
    if restart !=0:
        start = restart
    
    options = webdriver.ChromeOptions()

    # options.add_arguement('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36')
    options.add_argument("Accept=text/html,application/xhtml+xml,application/xml;q=0.9,imgwebp,*/*;q=0.8")
    driver = webdriver.Chrome('c:/chromedriver', options=options)
    driver.get('https://v4.map.naver.com/')   
    driver.add_cookie(driver.get_cookies()[0])

    # '오늘 하루 그만 보기' 체크박스 xpath : //*[@id="dday_popup"]/div[2]/div[2]/label/span
    elem_checkbox = driver.find_element_by_xpath('//*[@id="dday_popup"]/div[2]/div[2]/label/span')

    # 체크박스가 체크되어있지 않으면 클릭
    if not elem_checkbox.is_selected():
        elem_checkbox.click()

    # x버튼 xpath : //*[@id="dday_popup"]/div[2]/button/span[1]
    # 창닫기 x버튼 클릭
    driver.find_element_by_xpath('//*[@id="dday_popup"]/div[2]/button/span[1]').click()
    
    global count_success
    global count_over_fifty
    global count_search_zero
    global count_avoid_capcha
    global count_service_error
    
    count_success = 0
    count_over_fifty = 0
    count_search_zero = 0
    count_avoid_capcha = 0
    count_service_error = 0

    for i in tqdm.tnrange(len(dataframe[start:end])):
        try:
            tmp = crawl_naver_map_v4(dataframe[start:end].iloc[i], driver)

        except (exceptions.StaleElementReferenceException, exceptions.NoSuchElementException):
            clipboard_input('//*[@id="id"]', login.get("id"))
            clipboard_input('//*[@id="pw"]', login.get("pw"))
            driver.find_element_by_xpath('//*[@id="log.login"]').click()
            driver.implicitly_wait(3)
            time.sleep(0.5)
            
            count_avoid_capcha+=1
            print('캡차 우회 !!')
            print(f'성공 : {count_success} | 0건 검색 : {count_search_zero} | 50건이상 검색 : {count_over_fifty} | 캡챠 우회 : {count_avoid_capcha} | 서비스 오류 : {count_service_error}\n')
            
            tmp = crawl_naver_map_v4(dataframe[start:end].iloc[i], driver)
            
        
        except exceptions.ElementClickInterceptedException:
            error_button_xpath = """//*[@id="simplemodal-data"]/div[2]/a"""
            driver.find_element_by_xpath(error_button_xpath).click()
            driver.implicitly_wait(3)
            time.sleep(0.5)
            
            count_service_error+=1
            print('서비스 오류 발생 !!')
            print(f'성공 : {count_success} | 0건 검색 : {count_search_zero} | 50건이상 검색 : {count_over_fifty} | 캡챠 우회 : {count_avoid_capcha} | 서비스 오류 : {count_service_error}\n')
            tmp = crawl_naver_map_v4(dataframe[start:end].iloc[i], driver)

    driver.close()
    print('\n검색 종료!')

    global tmp_naver_search_all  # 검색결과 저장 DF 전역변수 사용
    global tmp_naver_search_rejected  # 검색거부 저장 DF 전역변수 사용

    tmp = tmp_naver_search_all, tmp_naver_search_rejected
    return tmp    