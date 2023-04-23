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
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from crawlerError import CrawlerError
import s3Manager
from logger import Logger
import os

from config.save_path import *

class NaverWebtoonCrawler : 
    def __init__(self):
        self.create_directory(STORAGE_DIR)
        self.create_directory(LOG_STORAGE_DIR)
        self.logger = Logger('crawlerlogger')
        self.logger.set_file_and_stream_handler(CRAWLER_LOG_FILE_PATH)
        self.s3_manager = s3Manager.S3Manager() 
        self.driver = self.create_chromedriver()


    def create_chromedriver(self) :
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ["enable-logging"])
        chrome_options.add_argument('user-agent=' + user_agent)

        try:
            driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException as e:
            self.logger.error(f"Error while creating chromedriver: {e}")
            driver = None
        
        self.logger.info("Complete to create chromedriver")
        return driver


    def create_directory(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info("Complete to create directory")
        except OSError:
            self.logger.error("Error: Failed to create the directory.")


    def get_toonURL_by_day(self, day:str) -> list: # 메인 홈에서 웹툰 titlID URL 수집
        toonURLs = []
        url = 'https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week='+day

        try : 
            self.driver.get(url)
            webtoon_list  = self.driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_list_toon > ul > li')
        
            for webtoon in webtoon_list  : 
                if webtoon.get_attribute('class') == 'item ': 
                    link = webtoon.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
                    toon_url = link.split('&')[0] 
                    toonURLs.append(toon_url)

        except NoSuchElementException as e:
            self.logger.error(f"Element not found: {e}")
        except TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
        except WebDriverException as e:
            self.logger.error(f"Web driver error: {e}")

        self.logger.info(f"Complete to get_toonURL_by_day: {day}")
        return toonURLs


    def get_and_save_weekly_toonURL(self) -> bool: # 수집한 toonURL pickle 형태로 저장 
        total_toonURL = []
        week =  ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        try:
            for day in week : 
                day_toonURL = self.get_toonURL_by_day(day) 
                total_toonURL.extend(day_toonURL) # extend로 list에 list 추가
                time.sleep(0.5)

            # 중복 제거
            self.logger.debug(f'중복 제거 전 길이 : {len(total_toonURL)}')
            total_toonURL = list(set(total_toonURL))
            self.logger.debug(f'중복 제거 후 길이 : {len(total_toonURL)}')    

            # 최종 웹툰 url 리스트 객체 저장 (pickle)
            with open(WEEKLY_TOONURL_PICKLE_FILE, 'wb') as f : 
                pickle.dump(total_toonURL, f)
            self.logger.info("Complete to get_and_save_weekly_toonURL")
            return True
        except Exception as e:
            self.logger.critical("Error occurred while saving the URLs: ", e)
            return False


    def load_weekly_toonURL(self) -> list: # 저장한 toonURL pickle 불러오기
        with open(WEEKLY_TOONURL_PICKLE_FILE, 'rb') as f : 
            weekly_toonURL = pickle.load(f)
        self.logger.info("Complete to load_weekly_toonURL")
        return weekly_toonURL


    def get_weekly_toon_info(self, total_toonURL:list) -> dict:  # 웹툰 정보 가져옴
        total_toon_info = {"title_id": [], "title": [], "summary": [], "author": [], "score": [], "favorite_count": [], "episode_count": [], "genre": [], "genre_detail": [], "week_days": []}
        
        for toon_url in total_toonURL : 
            title_id = toon_url.split('=')[1] 
            try : 
                self.driver.get(toon_url)
                title = self.driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/strong').text
                summary  = self.driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[1]').text
                author = self.driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[2]').text
                score =  self.driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.score').text
                favorite_count = self.driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.favcount > span.count_num').text
                episode_count = self.driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_episode_count > h3 > span').text
                genre = self.driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > span').get_attribute('textContent')
                genre_detail = self.driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > ul > li').get_attribute('textContent')
                week_days = []
                week_days_li = self.driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.week_day > dd > ul:nth-child(1) > li')
                for day in week_days_li : 
                    week_days.append(day.get_attribute('textContent')) 

                total_toon_info["title_id"].append(title_id)
                total_toon_info["title"].append(title)
                total_toon_info["summary"].append(summary)
                total_toon_info["author"].append(author)
                total_toon_info["score"].append(score)
                total_toon_info["favorite_count"].append(favorite_count)
                total_toon_info["episode_count"].append(episode_count)
                total_toon_info["genre"].append(genre)
                total_toon_info["genre_detail"].append(genre_detail)
                total_toon_info["week_days"].append(week_days)
                time.sleep(0.8)
            except NoSuchElementException as e:
                self.logger.error(f"[{title_id}] Element not found: {e}")

        self.logger.info("Complete to get_weekly_toon_info")
        return total_toon_info


    def save_weekly_toon_info_csv(self, total_toon_info:list) -> None : 
        df = pd.DataFrame(total_toon_info)
        df.to_csv(WEEKLY_TOONURL_INFO_FILE, encoding = "utf-8")
        self.logger.info("Complete to save_weekly_toon_info_csv")


    def load_total_toon_info(self):
        df = pd.read_csv(WEEKLY_TOONURL_INFO_FILE, encoding = "utf-8")
        self.logger.info("Complete to load_total_toon_info")
        return df

    '''
    여기 test중
    '''
    def get_epi_best_comments(self, title_id: str, epi_no: str) -> dict : # 특정 회차의 best 댓글만 수집
        try: 
            episode_url = 'https://comic.naver.com/webtoon/detail?titleId={tid}&no={epi}'.format(tid=title_id, epi=epi_no)
            self.driver.get(episode_url)

            epi_best_comments = {}

            list_comment = self.driver.find_elements(by=By.CSS_SELECTOR, value='#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li')
            for item in list_comment : 
                comment = item.find_element(by=By.CLASS_NAME, value='u_cbox_contents').text
                nickname  = item.find_element(by=By.CLASS_NAME, value='u_cbox_nick').text
                login_id = item.find_element(by=By.CLASS_NAME, value='u_cbox_id').text[1:-1]
                reply_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_reply_cnt').text
                recomm_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_cnt_recomm').text
                unrecomm_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_cnt_unrecomm').text
                write_date = item.find_element(by=By.CLASS_NAME, value='u_cbox_date').get_attribute('data-value')
                save_date = str(datetime.now().timestamp())
                is_best = True
                comment_uid = str(title_id) + str(epi_no) + '_' + str(login_id)[:4]  # 고유 값

                comment_dict = {}
                comment_dict['title_id'] = title_id
                comment_dict['epi_no'] = epi_no
                comment_dict['login_id'] = login_id
                comment_dict['nickname'] = nickname
                comment_dict['comment'] = comment
                comment_dict['reply_cnt'] = reply_cnt
                comment_dict['recomm_cnt'] = recomm_cnt
                comment_dict['unrecomm_cnt'] = unrecomm_cnt
                comment_dict['write_date'] = write_date
                comment_dict['save_date'] = save_date
                comment_dict['is_best'] = is_best

                epi_best_comments[comment_uid] = comment_dict
        except Exception as e:    
            self.logger.critical(f'Cannot get best comment in {title_id}/{epi_no}'.format(title_id=title_id, epi_no=epi_no)) 
            raise CrawlerError(str(e), title_id, epi_no) from e

        self.logger.info(f'Complete to get_epi_best_comments in {title_id}/{epi_no}'.format(title_id=title_id, epi_no=epi_no))
        return epi_best_comments


    def load_epi_best_comments(self, title_id : str, epi_no: str):
        file_name = '{title_id}/{title_id}_{epi_no}_best.json'.format(title_id=title_id,epi_no=epi_no)
        json_result = self.s3_manager.load_json_from_s3(file_name)
        self.logger.info("Complete to load_epi_best_comments")
        return json_result


    def get_total_comments(driver, title_id_list, epi_cnt_list) : # 전체 댓글 수집

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


    def main(self):
        # 0. WebDriver 생성 -> __init__ 으로 변경

        # 1. 요일별 toonURL 가려와서 pickle에 저장
        self.get_and_save_weekly_toonURL()

        # 2-. 최종 웹툰 url 리스트 객체 불러오기 (pickle) -> 함수화 load_weekly_toonURL()
        weekly_toonURL = self.load_weekly_toonURL()

        # 2. 웹툰 별 url 접속하여 정보 가져와 csv에 저장 (성인 웹툰 제외) -> 함수화 save_toon_info_csv()
        total_toon_info = self.get_weekly_toon_info(weekly_toonURL)
        self.save_weekly_toon_info_csv(total_toon_info)

        # 3. 위에서 저장한 데이터 불러오기 -> 함수화  load_total_toon_info()
        df = self.load_total_toon_info()
        title_id_list = df["title_id"]
        epi_cnt_list =  df["episode_count"] 
        
        # 4. 웹툰 별 회차별 url 접속하여 best 댓글 가져오기
        for title_id, epi_cnt in zip(title_id_list, epi_cnt_list): 
            for epi_no in range(1, epi_cnt + 1) :
                epi_best_comments = self.get_epi_best_comments(title_id, epi_no)
                file_name = '{title_id}/{title_id}_{epi_no}_best.json'.format(title_id=title_id,epi_no=epi_no)
                result = self.s3_manager.save_json_to_s3(file_name, epi_best_comments)
                time.sleep(1.0)
            time.sleep(1.5)
        
        self.driver.quit()
