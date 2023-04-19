from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pickle
import time 
import pandas as pd 
import boto3


from config.s3_credential import  AWS_ACCESS_KEY_ID ,AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION


def create_driver() :
    # 옵션 추가
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option('excludeSwitches', ["enable-logging"])

    # 연결 설정 
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    
    time.sleep(1)
    return driver

def get_list_toonURL(driver, url) : # 메인 홈에서 웹툰 titlID URL 슈집
    list_toonURL = []

    driver.get(url)
    list_toon = driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_list_toon > ul > li')
    
    # item_banner 제외한 item(웹툰)만 가져와서 url 링크 얻기 
    for item in list_toon : 
        if item.get_attribute('class') == 'item ': 
            link = item.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
            toon_url = link.split('&')[0] # 뒤에 요일 파라미터 제거 
            print(toon_url)
            list_toonURL.append(toon_url)

    return list_toonURL


def save_toon_info(driver, total_toonURL) :  # 웹툰 정보 CSV 저장

    title_id_list = []
    title_list = []
    summary_list = []
    author_list = []
    score_list = []
    count_num_list = []
    episode_count_list = []
    genre_list = []
    genre_detail_list = []
    week_days_list = []

    ban_toonid_list = []
    # 웹툰 정보 크롤링 
    cnt = 1
    for toon_url in total_toonURL : 
        title_id = toon_url.split('=')[1] 
        print(f'cnt : {cnt} titleId : {title_id}')
        cnt += 1
        try : 
            driver.get(toon_url)

            title = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/strong').text
            summary  = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[1]').text
            author = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[2]').text
            score =  driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.score').text
            count_num = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.favcount > span.count_num').text
            episode_count = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_episode_count > h3 > span').text

            # genre, genre_detail. week_days의 경우 'display:block'이라 .text로 접근 불가 -> get_attribute('textContent') 으로 데이터 가져옴
            genre = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > span').get_attribute('textContent')
            genre_detail = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > ul > li').get_attribute('textContent')

            week_days = []
            week_days_li = driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.week_day > dd > ul:nth-child(1) > li')
            for day in week_days_li : 
                week_days.append(day.get_attribute('textContent')) 

            title_id_list.append(title_id)
            title_list.append(title)
            summary_list.append(summary)
            author_list.append(author)
            score_list.append(score)
            count_num_list.append(count_num)
            episode_count_list.append(episode_count)
            genre_list.append(genre)
            genre_detail_list.append(genre_detail)
            week_days_list.append(week_days)
            
            time.sleep(0.5)

        except Exception as e:    
            ban_toonid_list.append(title_id)
            print('예외가 발생했습니다. title_id : ', title_id,  e)
            # return False
        time.sleep(0.4)

    total_toon_info = {"title_id" : title_id_list, "title" : title_list ,"summary" : summary_list, "author" : author_list,"score" : score_list,"count_num" : count_num_list,"episode_count" : episode_count_list, "genre" : genre_list,"genre_detail" : genre_detail_list, "week_days" : week_days_list}
    df = pd.DataFrame(total_toon_info)
    print(df.head(5))
    df.to_csv("total_toon_info_v3.csv", encoding = "utf-8-sig")


def get_best_comments(driver, title_id_list, epi_cnt_list) : # best 댓글만 수집

    for title_id, epi_cnt in zip(title_id_list, epi_cnt_list): 
        print(title_id, epi_cnt)

        # 한 웹툰 -> 여러 회차 정보 불러오기
        for epi_no in range(1, epi_cnt + 1) :
            title_id_list = [] 
            epi_no_list = []
            comments_list = []
            nickname_list = []
            login_id_list = []
            reply_cnt_list = []
            recomm_cnt_list = []
            unrecomm_cnt_list = []
            write_date_list = []
            save_date_list = []
            isbest_list = []

            if epi_no == 6 : #Test용
                break
            episode_url = 'https://comic.naver.com/webtoon/detail?titleId=' + str(title_id) + '&no=' + str(epi_no)
            driver.get(episode_url)

            # 총 댓글 갯수
            # comments_num = driver.find_element(by=By.CSS_SELECTOR, value='#cbox_module > div > div.u_cbox_head > span').text
            # print(f'comments_num : {comments_num}')

            # # BEST 댓글 정보 가져오기
            list_comment = driver.find_elements(by=By.CSS_SELECTOR, value='#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li')
            for item in list_comment : 
                # print("item : " ,  item)

                comment = item.find_element(by=By.CLASS_NAME, value='u_cbox_contents').text
                nickname  = item.find_element(by=By.CLASS_NAME, value='u_cbox_nick').text
                login_id = item.find_element(by=By.CLASS_NAME, value='u_cbox_id').text[1:-1]
                reply_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_reply_cnt').text
                recomm_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_cnt_recomm').text
                unrecomm_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_cnt_unrecomm').text
                write_date = item.find_element(by=By.CLASS_NAME, value='u_cbox_date').text
                # print(comment)
                
                title_id_list.append(title_id)
                epi_no_list.append(epi_no)
                comments_list.append(comment)
                nickname_list.append(nickname)
                login_id_list.append(login_id)
                reply_cnt_list.append(reply_cnt)
                recomm_cnt_list.append(recomm_cnt)
                unrecomm_cnt_list.append(unrecomm_cnt)
                write_date_list.append(write_date)
                save_date_list.append(datetime.now())
                isbest_list.append(True)

            epi_best_comments = {"title_id" : title_id_list,"epi_no" : epi_no_list,"comment" : comments_list,"nickname" : nickname_list,"login_id" : login_id_list,"reply_cnt" : reply_cnt_list ,"recomm_cnt" : recomm_cnt_list,"unrecomm_cnt" : unrecomm_cnt_list ,"write_date" : write_date_list,"save_date" : save_date_list,"is_best" :isbest_list}
            df = pd.DataFrame(epi_best_comments)
            print(df.head(5))
            file_name = str(title_id)+ '_' + str(epi_no) + '.csv'
            df.to_csv(file_name, encoding = "utf-8-sig")
            # print("epi_best_comments :", epi_best_comments)

            time.sleep(1)
            # break


def upload_json_obj_s3(data, bucket_name, object_key): # json 객체 저장 
    s3 = boto3.resource('s3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    # 데이터를 이진 데이터로 직렬화
    binary_data = pickle.dumps(data)
    print("binary_data : ", binary_data)

    # S3에 데이터 저장
    try:
        s3.Object(bucket_name, object_key).put(Body=binary_data)
        print("저장 완료됨")
        return True
    except :
        return False


def upload_json_file_s3(bucket, file_name, json_file):  # json 파일 저장 
    encode_file = bytes(json.dumps(json_file).encode('UTF-8'))
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket, Key=file_name, Body=encode_file)
        return True
    except:
        return False
    

def upload_csv_file_s3(bucket, file_name, csv_file):  # csv 파일 저장 
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket, Key=file_name, Body=csv_file)
        return True
    except:
        return False


def get_save_toonurl(driver): # 수집한 toonURL pickle 형태로 저장 
    total_toonURL = []
    week =  ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    for day in week : 
        url = 'https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week='+day
        day_toonURL = get_list_toonURL(driver, url) 
        total_toonURL.extend(day_toonURL) # extend로 list에 list 추가
        time.sleep(0.5)

    # 중복 제거
    print(f'중복 제거 전 길이 : {len(total_toonURL)}')
    total_toonURL = set(total_toonURL)
    print(f'중복 제거 후 길이 : {len(total_toonURL)}')
    print(f'최종 웹툰 url 리스트 : \n {total_toonURL}')

    print("total_toonURL : ", total_toonURL)

    # 최종 웹툰 url 리스트 객체 저장 (pickle)
    with open('data.pickle', 'wb') as f : 
        pickle.dump(total_toonURL, f)


if __name__ == "__main__" : 
    # 0. WebDriver 생성
    driver = create_driver()

    # 1. 요일별 toonURL 가려와서 pickle에 저장
    get_save_toonurl(driver)

    # 2-. 최종 웹툰 url 리스트 객체 불러오기 (pickle)
    total_toonURL = []
    with open('data.pickle', 'rb') as f : 
        total_toonURL = pickle.load(f)
    
    # (test용).txt 파일에 저장 
    # with open("total_toonURL.txt", 'w', encoding='UTF-8') as f:
    #     for toon in total_toonURL :
    #         f.write(toon +'\n')
    

    # 2. 웹툰 별 url 접속하여 정보 가져와 csv에 저장 (성인 웹툰 제외)    
    save_toon_info(driver, total_toonURL)

    # 위에서 저장한 데이터 불러오기
    csv = pd.read_csv("total_toon_info_v3.csv", encoding = "utf-8-sig")


    # 3. 웹툰 별 회차별 url 접속하여 best 댓글 가져오기
    get_best_comments(driver, csv["title_id"], csv["episode_count"]  )
    driver.quit()


    # for title_id, epi_cnt in zip(csv["title_id"], csv["episode_count"] ): 
    #     print(title_id, epi_cnt)
    #     for epi_no in range(1, epi_cnt + 1) :
    #         episode_url = 'https://comic.naver.com/webtoon/detail?titleId=' + str(title_id) + '&no=' + str(epi_no)
    #         get_best_comments(driver, episode_url)
    #         get_best_comments(driver, title_id_list, epi_cnt_list )
    #         time.sleep(1)

    # driver.quit()

######################[s3 test]
    # # 데이터 크롤링
    # data = {'key1': 'value1', 'key2': 'value2'}

    # # S3에 데이터 저장
    
    # bucket_name = 'naverwebtoon'
    # object_key = 'test.pickle'
    # upload_json_obj_s3(data, bucket_name, object_key)

    # # client = boto3.client('s3',
    # #                   aws_access_key_id=AWS_ACCESS_KEY_ID,
    # #                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    # #                   region_name=AWS_DEFAULT_REGION
    # #                   )

    # # response = client.list_buckets() # bucket 목록
    # # print(response)