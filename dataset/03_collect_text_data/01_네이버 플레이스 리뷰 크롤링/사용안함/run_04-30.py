from bs4 import BeautifulSoup
import requests
import urllib.request
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from tqdm import tqdm, tqdm_notebook
import time
import os
from datetime import datetime
import random
from threading import Thread

def crawler(start, end, thread_id):
    path = 'd:/marytalk/naver_map_seoul_salon_output_data_2020-04-29_final.csv'
    headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64)    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36", 
                "Accept":"text/html,application/xhtml+xml,application/xml;\
                q=0.9,imgwebp,*/*;q=0.8"}
    #업소 CSV파일 불러오기
    salonDF = pd.read_csv(path, index_col=0)
    #store_id 에서 s 제거 후 store_id와 store_name 컬럼을 데이터프레임으로 저장
    # salonDF.store_id=salonDF['store_id'].str.lstrip("s")
    salonDF = salonDF[['store_id', 'store_id_only_num', 'store_name']]
    baseurl = 'https://store.naver.com/hairshops/detail?id='
    rows=[]
    rejects=[]
    
    
    for code_index in tqdm(range(start, end)):
        time.sleep(random.uniform(1,8)+np.random.rand())
        error_type=0
        retry_count=0
        while 1 :
            count_list = []
            count_list.append(salonDF.store_id[code_index])
            count_list.append(salonDF.store_id_only_num[code_index])
            count_list.append(salonDF.store_name[code_index])
            
            # 예약자리뷰, 영수증리뷰, 블로그리뷰 페이지수 크롤링
            for tab in ['bookingReview','receiptReview','fsasReview'] :
                url = baseurl + str(count_list[1]) + '&tab=' + tab
                response = requests.get(url, headers=headers)
                time.sleep(random.uniform(8,12)+np.random.rand())
                naver_place = BeautifulSoup(response.text, 'lxml')
                time.sleep(np.random.rand())
                
                # request 실패
                if response.status_code != 200 :
                    # 페이지 에러
                    # 해당 업소 결과에 np.nan 넣고 error_type=1인 경우로 이동
                    if naver_place.text.split('\n')[0] =='네이버 :: 페이지를 찾을 수 없습니다.':
                        print(f"\n[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name {count_list[2]} \t[페이지 요청 실패 - 페이지 없음]")
                        error_type=1
                        count_list.append(np.nan)
                        count_list.append(np.nan)
                        count_list.append(np.nan)
                        break
                    # 접속 에러
                    else :
                        error_type=2
                        retry_count+=1
                        print(f"\n[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name : {count_list[2]} \t[페이지 요청 실패 - 접속 에러]")
                        time.sleep(np.random.rand())
                        break
                        
                # request 성공
                else :
                    try :
                        error_type=0
                        lastpage = naver_place.find('span', class_='total').get_text()
                    except AttributeError :
                        lastpage = 1
                    print(f'\n[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name : {count_list[2]} \t[페이지 요청 성공]')
                    count_list.append(lastpage)
            
            
            #for문이 정상적으로 종료된 경우
            if error_type == 0 :
                rows.append(count_list)
                ndf = DataFrame(rows, columns=['store_id', 'store_id_only_num', 'store_name', 'booking','receipt','blog'])
                ndf.to_csv("./naver_place_count(%i-%i).csv" %(start, end-1), sep=',', encoding='utf-8-sig')
                print(f'[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name : {count_list[2]} \t[저장 성공 !! (정상 작업)] - 페이지수 : {count_list[3:]} \n')
                break
            
            # 페이지 에러
            # page가 np.nan값 밖에 없으면 종료 / 아닌 경우 다시 탐색
            elif error_type == 1:
                if len(count_list)==6 :                  
                    rows.append(count_list)
                    ndf = DataFrame(rows, columns=['store_id', 'store_id_only_num', 'store_name', 'booking','receipt','blog'])
                    ndf.to_csv("./naver_place_count(%i-%i).csv" %(start, end-1), sep=',', encoding='utf-8-sig')
                    print(f'\n[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name : {count_list[2]} \t[저장 성공 !! (페이지 없음)] - 페이지수 : {count_list[3:]}\n')
                    break
                else :
                    continue
                    
            # 접속 에러 - 재시도
            # 5회 재시도 실패하면 해당 업소 결과에 np.nan 넣고 턴 종료
            elif error_type == 2 :
                if retry_count==10 :
                    count_list.append(np.nan)
                    count_list.append(np.nan)
                    count_list.append(np.nan)
                    rejects.append(count_list[:6])
                    reject_df = DataFrame(rejects, columns=['store_id', 'store_id_only_num', 'store_name', 'booking','receipt','blog']) 
                    reject_df.to_csv("./reject_naver_place(%i-%i).csv" %(start, end-1), sep=',', encoding='utf-8-sig')
                    print(f"\n[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name : {count_list[2]} \t[저장 성공 !! (페이지 요청 재시도 5회 실패)] - 페이지수 : {count_list[3:]}\n")
                    break
                else:
                    print(f"[thread {thread_id}] 인덱스 : {code_index} | store_id : {count_list[0]} | store_name : {count_list[2]} \t[페이지 접속 에러 - 재시도 : {retry_count} 회]\n")
                    continue
            
            
    
    

if __name__ == '__main__':
    start, end = 0, 13398
    step = np.linspace(start, end, 31, dtype=int)
    ths = []
    start_time = time.time()
    
    for i in range(0,30) :
        th = Thread(target=crawler, args=(step[i], step[i+1], i+1))
        ths.append(th)
        time.sleep(np.random.rand())
        th.start()
    
    for th in ths :
        th.join()
        
    end_time = time.time()
    print(end_time-start_time)