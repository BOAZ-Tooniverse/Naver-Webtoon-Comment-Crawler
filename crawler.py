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
    driver.get(toon_url)

    # 웹툰 정보 크롤링 
    print("\n\n===============================================")
    title_id = toon_url.split('=')[1] 
    print(f'title_id : {title_id}')
    title = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/strong')
    print(f'title : {title.text}')
    summary = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[1]')
    print(f'summary : {summary.text}')
    author = driver.find_element(by=By.XPATH, value='//*[@id="ct"]/div[1]/div[1]/div[1]/span[2]')
    print(f'author : {author.text}')
    score = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.score')
    print(f'score : {score.text}')
    count_num = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_front.is_active.anim_on > div.area_info > span.detail > span.favcount > span.count_num')
    print(f'count_num : {count_num.text}')
    
    genre = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > span').get_attribute('textContent')
    print(f'genre : {genre}')
    genre_detail = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.genre > dd > ul > li').get_attribute('textContent')
    print(f'genre_detail : {genre_detail}')

    week_days = []
    week_days_li = driver.find_elements(by=By.CSS_SELECTOR, value='#ct > div.section_toon_info > div.info_back > dl > div.week_day > dd > ul:nth-child(1) > li')
    for day in week_days_li : 
        week_days.append(day.get_attribute('textContent'))
    print(f'week_days : {week_days}')    
    
    episode_count = driver.find_element(by=By.CSS_SELECTOR, value='#ct > div.section_episode_count > h3 > span')
    print(f'episode_count : {episode_count.text}')

    
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

    # 2. 웹툰 별 url 접속하여 정보 가져오기
    for toonURL in total_toonURL :
        get_toon_info(driver, toonURL)


    time.sleep(4) 
    driver.quit()