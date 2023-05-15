import pickle
import time
import logging
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, NoSuchElementException, TimeoutException
from logger.crawler_logger import CrawlerLogger
from config.save_path import WEEKLY_TOONURL_PICKLE_FILE, WEEKLY_TOONURL_LOG_FILE
from crawler.constants import WEEK_TOONURL
from crawler.chrome_driver import ChromeDriver


class WeeklyToonurlCrawler:
    """
    네이버 웹툰의 주간 웹툰(월-금)의 URL을 크롤링하고 저장 및 불러오는 함수로 구성된 클래스
    """

    def __init__(self):
        self.logger = CrawlerLogger('weeklytoonurl', logging.DEBUG, WEEKLY_TOONURL_LOG_FILE)
        self.driver = ChromeDriver()

    def get_toonurl_by_day(self, day:str) -> list:
        """
        메인 홈에서 웹툰 titlID URL 수집하는 함수
        """
        total_toonurl = []
        url = WEEK_TOONURL + day

        try :  
            self.driver.start()
            self.driver.get_driver().get(url)
            webtoon_list  = self.driver.get_driver().find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_list_toon > ul > li')
        
            for webtoon in webtoon_list :
                if webtoon.get_attribute('class') == 'item ': 
                    link = webtoon.find_element(by=By.TAG_NAME, value='a').get_attribute('href')
                    toon_url = link.split('&')[0]
                    total_toonurl.append(toon_url)

        except NoSuchElementException as e:
            self.logger.error(f"Element not found: {e}")
        except TimeoutException as e:
            self.logger.error(f"Timeout error: {e}")
        except WebDriverException as e:
            self.logger.error(f"Web driver error: {e}")
        finally:
            self.driver.stop()
        self.logger.info(f"Complete to get_toonURL_by_day: {day}")
        
        return total_toonurl

    def get_and_save_weekly_toonurl(self) -> bool:
        """
        수집한 toonURL pickle 형태로 저장하는 함수
        """
        weekly_toonurl = []
        week =  ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        try:
            for day in week : 
                day_toonurl = self.get_toonurl_by_day(day) 
                weekly_toonurl.extend(day_toonurl) # extend로 list에 list 추가
                time.sleep(0.5)

            # 중복 제거
            self.logger.debug(f'중복 제거 전 길이 : {len(weekly_toonurl)}')
            weekly_toonurl = list(set(weekly_toonurl))
            self.logger.debug(f'중복 제거 후 길이 : {len(weekly_toonurl)}')    

            # 최종 웹툰 url 리스트 객체 저장 (pickle)
            with open(WEEKLY_TOONURL_PICKLE_FILE, 'wb') as f : 
                pickle.dump(weekly_toonurl, f)
            self.logger.info("Complete to get_and_save_weekly_toonURL")
            return True
        except Exception as e:
            self.logger.critical("Error occurred while saving the URLs: ", e)
            return False    
    
    def load_weekly_toonurl(self) -> list : 
        """
        저장한 toonURL pickle 불러오는 함수
        """
        with open(WEEKLY_TOONURL_PICKLE_FILE, 'rb') as f : 
            weekly_toonurl = pickle.load(f)
        self.logger.info("Complete to load_weekly_toonURL")
        return weekly_toonurl