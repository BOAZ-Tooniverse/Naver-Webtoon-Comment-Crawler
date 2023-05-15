import os
from crawler.weekly_tooninfo_crawler import *
from crawler.weekly_toonurl_crawler import *
from crawler.best_comment_crawler import *
from config.save_path import STORAGE_DIR, LOG_STORAGE_DIR

def create_directory(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print("Complete to create directory")
        except OSError:
                print("Error: Failed to create the directory.")

def all_steps():
    """
    크롤링 모든 절차를 구현한 함수
    """
    # 0. 디렉토리 생성
    create_directory(STORAGE_DIR)
    create_directory(LOG_STORAGE_DIR)

    # 1. 요일별 toonURL 가려와서 pickle에 저장
    toonurl_crawler = WeeklyToonurlCrawler()
    if not toonurl_crawler.get_and_save_weekly_toonurl() :
        print("에러 발생")
        return False

    # 2. 최종 웹툰 url 리스트 객체 불러오기 (pickle) -> 함수화 load_weekly_toonURL()
    weekly_toonurl = toonurl_crawler.load_weekly_toonurl()

    # 3. 웹툰 별 url 접속하여 정보 가져와 csv에 저장 (성인 웹툰 제외) -> 함수화 save_toon_info_csv()
    tooninfo_crawler = WeeklyToonInfoCrawler()
    total_toon_info = tooninfo_crawler.get_weekly_tooninfo(weekly_toonurl)
    if not tooninfo_crawler.save_weekly_tooninfo_csv(total_toon_info):
        print("에러발생")   
        return False

    # 4. 위에서 저장한 데이터 불러오기 
    total_toon_info_df = tooninfo_crawler.load_total_tooninfo()
    
    # 5. 웹툰 별 회차별 url 접속하여 best 댓글 가져오기
    best_comment_crawler = BestCommentCrawler()
    best_comment_crawler.get_and_save_all_best_comments(title_id_list=total_toon_info_df["title_id"], epi_cnt_list=total_toon_info_df["episode_count"])

def get_best_comments():
    # 0. 디렉토리 생성
    create_directory(STORAGE_DIR)
    create_directory(LOG_STORAGE_DIR)

    # 1. 위에서 저장한 데이터 불러오기 
    tooninfo_crawler = WeeklyToonInfoCrawler()
    total_toon_info_df = tooninfo_crawler.load_total_tooninfo()
    
    # 2. 웹툰 별 회차별 url 접속하여 best 댓글 가져오기
    best_comment_crawler = BestCommentCrawler()
    best_comment_crawler.get_and_save_all_best_comments(title_id_list=total_toon_info_df["title_id"], epi_cnt_list=total_toon_info_df["episode_count"])

if __name__ == "__main__" : 
    get_best_comments()
