import time
import logging
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from logger.crawler_logger import CrawlerLogger
from config.save_path import WEEKLY_TOONINFO_LOG_FILE, WEEKLY_TOONURL_INFO_FILE
from crawler.chrome_driver import ChromeDriver


class WeeklyToonInfoCrawler: 
    """
    네이버 웹툰의 특정 웹툰의 정보를 크롤링하고 저장 및 불러오는 함수로 구성된 클래스
    """

    def __init__(self):
        self.logger = CrawlerLogger('weeklytooninfo', logging.DEBUG, WEEKLY_TOONINFO_LOG_FILE)
        self.driver = ChromeDriver()

    def get_weekly_tooninfo(self, weekly_toonurl:list) -> dict:  
        """
        네이버 웹툰 url에 접속하여 웹툰 정보 크롤링하는 함수  
        """ 
        total_toon_info = {"title_id": [], "title": [], "summary": [], "author": [], "score": [], "favorite_count": [], "episode_count": [], "genre": [], "genre_detail": [], "week_days": []}
        
        for toon_url in weekly_toonurl:
            title_id = toon_url.split('=')[1]
            try: 
                self.driver.start()
                self.driver.get_driver().get(toon_url)
                title = self.driver.get_driver().find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/strong').text
                summary  = self.driver.get_driver().find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[1]').text
                author = self.driver.get_driver().find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[2]').text
                score =  self.driver.get_driver().find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.score').text
                favorite_count = self.driver.get_driver().find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.favcount > span.count_num').text
                episode_count = self.driver.get_driver().find_element(by=By.CSS_SELECTOR, value='#ct > div.section_episode_count > h3 > span').text
                genre = self.driver.get_driver().find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > span').get_attribute('textContent')
                genre_detail = self.driver.get_driver().find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > ul > li').get_attribute('textContent')
                week_days = []
                week_days_li = self.driver.get_driver().find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.week_day > dd > ul:nth-child(1) > li')
                for day in week_days_li: 
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
            finally:
                self.driver.stop()

        self.logger.info("Complete to get_weekly_toon_info")
        return total_toon_info

    def save_weekly_tooninfo_csv(self, total_toon_info:list) -> None: 
        """
        네이버 주간 웹툰 정보를 csv로 저장하는 함수
        """
        try:
            if not isinstance(total_toon_info, list):
                raise TypeError("total_toon_info should be a list")
            df = pd.DataFrame(total_toon_info)
            with open(WEEKLY_TOONURL_INFO_FILE, mode='w', encoding='utf-8') as f:
                df.to_csv(f, index=False, header=True)
            self.logger.info("Complete to save_weekly_toon_info_csv")
            return True
        except TypeError as e:
            self.logger.error(f"TypeError: {str(e)}")
            return False
        except PermissionError as e:
            self.logger.error(f"PermissionError: {str(e)}")
            return False

    def load_total_tooninfo(self):
        """
        csv로 저장된 네이버 주간 웹툰 정보를 불러오는 함수
        """
        try:
            df = pd.read_csv(WEEKLY_TOONURL_INFO_FILE, encoding="utf-8")
            self.logger.info("Complete to load_total_toon_info")
            return df
        except FileNotFoundError as e:
            self.logger.error(f"{WEEKLY_TOONURL_INFO_FILE} does not exist. Error: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load {WEEKLY_TOONURL_INFO_FILE}. Error: {str(e)}")
            return None