import time
import logging
from datetime import datetime
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from logger.crawler_logger import CrawlerLogger
from error.crawler_error import CrawlerError
from config.save_path import BEST_COMMENT_LOG_FILE
from crawler.chrome_driver import ChromeDriver
from s3.s3_manager import S3Manager

class BestCommentCrawler :
    """
    네이버 웹툰의 특정 웹툰의 회차에서 best 댓글 크롤링하여 저장하는 함수로 구성된 클래스
    """

    def __init__(self):
        self.logger = CrawlerLogger('bestcomment', logging.DEBUG, BEST_COMMENT_LOG_FILE)
        self.driver = ChromeDriver()
        self.s3_manager = S3Manager() 

    def get_epi_best_comments(self, title_id: str, epi_no: str) -> dict:
        """
        특정 회차의 best 댓글들을 크롤링하는 함수
        """
        self.logger.debug(f'Start to get_epi_best_comments [epi : {title_id}]')

        try: 
            episode_url = 'https://comic.naver.com/webtoon/detail?titleId={tid}&no={epi}'.format(tid=title_id, epi=epi_no)
            epi_best_comments = {}
            
            self.driver.start()
            self.driver.get_driver().get(episode_url)

            # Turn Off CleanBot
            btn_cleanbot = WebDriverWait(self.driver.get_driver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cbox_module > div > div.u_cbox_cleanbot > a')))
            btn_cleanbot.click()
            time.sleep(0.5)
            btn_turn_off = WebDriverWait(self.driver.get_driver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#cleanbot_dialog_checkbox_cbox_module')))
            btn_turn_off.click()
            time.sleep(0.5)
            btn_check = WebDriverWait(self.driver.get_driver(), 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.u_cbox.u_cbox_layer_wrap > div > div.u_cbox_layer_cleanbot2 > div.u_cbox_layer_cleanbot2_extra > button')))
            btn_check.click()
            time.sleep(0.5)

            # Get Best Comments
            list_comment = WebDriverWait(self.driver.get_driver(), 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li')))            
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
                comment_uid = item.get_attribute('data-info').split("'")[1]

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
        except TimeoutException as e:
            self.logger.critical(f'TimeoutException: {str(e)}. Cannot get best comment in {title_id}/{epi_no}')
            raise CrawlerError(str(e), title_id, epi_no) from e
        except NoSuchElementException as e:
            self.logger.critical(f'NoSuchElementException: {str(e)}. Cannot get best comment in {title_id}/{epi_no}')
            raise CrawlerError(str(e), title_id, epi_no) from e 
        except Exception as e:    
            self.logger.critical(f'Cannot get best comment in {title_id}/{epi_no}'.format(title_id=title_id, epi_no=epi_no)) 
            raise CrawlerError(str(e), title_id, epi_no) from e
        finally:
            self.logger.debug(f'Complete to get_epi_best_comments in {title_id}/{epi_no}'.format(title_id=title_id, epi_no=epi_no))
            self.driver.stop()
        return epi_best_comments

    def get_and_save_all_best_comments(self, title_id_list : List, epi_cnt_list: List):
        """
        모든 웹툰의 회차 별 best 댓글들을 저장한 json파일을 s3에 저장하는 함수
        """
        idx = 1
        while idx < len(title_id_list):
            title_id = str(title_id_list[idx])
            epi_cnt = epi_cnt_list[idx]
            self.logger.info(f'Start to get_epi_best_comments [titleID : {title_id}]')
            for epi_no in range(1, epi_cnt + 1) :
                epi_best_comments = self.get_epi_best_comments(title_id, epi_no)
                file_name = '{title_id}/{title_id}_{epi_no}_best.json'.format(title_id=title_id,epi_no=epi_no)
                self.s3_manager.save_json_to_s3(file_name, epi_best_comments)
                time.sleep(0.3)
            idx += 1

    def load_epi_best_comments(self, title_id : str, epi_no: str):
        """
        특정 회차의 best 댓글들을 저장한 json파일을 s3에서 불러오는 함수
        """
        file_name = '{title_id}/{title_id}_{epi_no}_best.json'.format(title_id=title_id,epi_no=epi_no)
        json_result = self.s3_manager.load_json_from_s3(file_name)
        self.logger.info("Complete to load_epi_best_comments")
        return json_result