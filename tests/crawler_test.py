# from crawlers.webtoonCrawler import NaverWebtoonCrawler
# import time
# from selenium.webdriver.common.by import By

# def test_crawler_init():
#     crawler = NaverWebtoonCrawler()
#     url = 'https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=mon'
#     crawler.driver.get(url)
#     webtoon_list  = crawler.driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_list_toon > ul > li')
#     print(webtoon_list[0].text)

# '''
# TEST #1 : 주간 웹툰 titlID URL 저장 및 불러오기
# - get_toonURL_by_day() 메인홈에서 웹툰 titlID URL 수집
# - get_and_save_weekly_toonURL(): 위 함수 호출하여 toonURL pickle 형태로 저장 
# - load_weekly_toonURL() : 저장한 toonURL pickle 불러오기
# '''
# def test_get_and_save_weekly_toonURL():
#     crawler = NaverWebtoonCrawler()
#     crawler.get_and_save_weekly_toonURL()


# def test_load_weekly_toonURL():
#     crawler = NaverWebtoonCrawler()
#     weekly_toonURL = crawler.load_weekly_toonURL()
#     print(weekly_toonURL)
#     print(len(weekly_toonURL))
#     print(weekly_toonURL[-1])

# '''
# TEST #2 : 웹툰 상세 정보 저장하고 불러오기
# - get_weekly_toon_info() :  웹툰 하나씩 접속해 정보 가져옴
# - save_weekly_toon_info_csv() : 위 함수로 얻어온 정보를 csv로 저장함
# - load_total_toon_info() : 불러오기 
# '''
# def test_save_weekly_toon_info_csv() : 
#     crawler = NaverWebtoonCrawler()
#     weekly_toonURL = crawler.load_weekly_toonURL()
#     weekly_toon_info = crawler.get_weekly_toon_info(weekly_toonURL)
#     result = crawler.save_weekly_toon_info_csv(weekly_toon_info)
#     print(result)


# def test_load_total_toon_info() : 
#     crawler = NaverWebtoonCrawler()
#     df = crawler.load_total_toon_info()

#     title_id_list = df["title_id"]
#     epi_cnt_list =  df["episode_count"] 
#     print(title_id_list)
#     print(epi_cnt_list)


# '''
# TEST #3 : 특정 화의 best 댓글 가져오기 
# -
# '''
# def test_get_save_total_epi_best_comments():
#     crawler = NaverWebtoonCrawler()
#     df = crawler.load_total_toon_info()
#     title_id_list = df["title_id"]
#     epi_cnt_list =  df["episode_count"] 

#     for title_id, epi_cnt in zip(title_id_list, epi_cnt_list): 
#         for epi_no in range(1, epi_cnt + 1) :
#             epi_best_comments = crawler.get_epi_best_comments(title_id, epi_no)
#             file_name = '{title_id}/{title_id}_{epi_no}_best.json'.format(title_id=title_id,epi_no=epi_no)
#             result = crawler.s3_manager.save_json_to_s3(file_name, epi_best_comments)
#             # print( str(title_id)+ '_' + str(epi_no) + ' : ' + str(result))
#             break
#             time.sleep(1.0)
#         break
#         time.sleep(1.5)

# def test_get_one_epi_best_comments():
#     crawler = NaverWebtoonCrawler()
#     # 정상 
#     # title_id = "775334"
#     # epi_no = "2"
#     # 비정상 
#     title_id = "753842"
#     epi_no = "17"

#     epi_best_comments = crawler.get_epi_best_comments(title_id, epi_no)
#     print(epi_best_comments)


# def test_load_epi_best_comments():
#     title_id = "775334"
#     epi_no = "2"
#     crawler = NaverWebtoonCrawler()
#     result = crawler.load_epi_best_comments(title_id, epi_no)
#     print(result)


# if __name__ == "__main__" : 
#     # TEST #0
#     test_crawler_init() # OK

#     # TEST #1
#     # test_get_and_save_weekly_toonURL() # OK
#     # test_load_weekly_toonURL() # OK

#     # TEST #2
#     # test_save_weekly_toon_info_csv() # OK
#     # test_load_total_toon_info() # OK

#     # TEST #3
#     # test_get_save_total_epi_best_comments()
#     # test_get_one_epi_best_comments() 
#     # test_load_epi_best_comments() # Ok