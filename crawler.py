from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time 

def create_driver() :
    # 옵션 추가
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option('excludeSwitches', ["enable-logging"])

    # 연결 설정 
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    
    time.sleep(1)
    return driver

def get_list_toonURL(driver, url) :
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
    
def get_toon_info(driver, toon_url) : 
    webtoon_info = {}
    
    # 웹툰 정보 크롤링 
    driver.get(toon_url)

    webtoon_info['title_id'] = toon_url.split('=')[1] 
    webtoon_info['title'] = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/strong').text
    webtoon_info['summary']  = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[1]').text
    webtoon_info['author'] = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[2]').text
    webtoon_info['score'] =  driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.score').text
    webtoon_info['count_num'] = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.favcount > span.count_num').text
    webtoon_info['episode_count'] = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_episode_count > h3 > span').text

    # genre, genre_detail. week_days의 경우 'display:block'이라 .text로 접근 불가 -> get_attribute('textContent') 으로 데이터 가져옴
    webtoon_info['genre'] = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > span').get_attribute('textContent')
    webtoon_info['genre_detail'] = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > ul > li').get_attribute('textContent')

    week_days = []
    week_days_li = driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.week_day > dd > ul:nth-child(1) > li')
    for day in week_days_li : 
        week_days.append(day.get_attribute('textContent')) 
    webtoon_info['week_days'] = week_days

    return webtoon_info

    
def get_comments(driver, toon_episode_url) : 
    driver.get(toon_episode_url)


if __name__ == "__main__" : 
    # 0. WebDriver 생성
    driver = create_driver()

    # 1. 모든 웹툰 url 링크 저장하기 (요일별로 URL 접근)
    total_toonURL = []
    week =  ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    for day in week : 
        url = 'https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week='+day
        day_toonURL = get_list_toonURL(driver, url) 
        total_toonURL.extend(day_toonURL) # extend로 list에 list 추가

    # 중복 제거
    print(f'중복 제거 전 길이 : {len(total_toonURL)}')
    total_toonURL = set(total_toonURL)
    print(f'중복 제거 후 길이 : {len(total_toonURL)}')
    print(f'최종 웹툰 url 리스트 : \n {total_toonURL}')

    # 최종 웹툰 url 리스트 객체 저장 (pickle)
    with open('data.pickle', 'wb') as f : 
        pickle.dump(total_toonURL, f)
    

    # 2-. 최종 웹툰 url 리스트 객체 불러오기 (pickle)
    total_toonURL = []
    with open('data.pickle', 'rb') as f : 
        total_toonURL = pickle.load(f)

    # 2. 웹툰 별 url 접속하여 정보 가져오기 (문제 : 19세 웹툰 접근 불가)
    total_toon_info = []
    for toonURL in total_toonURL :
        total_toon_info.append(get_toon_info(driver, toonURL))

    time.sleep(4) 
    driver.quit()