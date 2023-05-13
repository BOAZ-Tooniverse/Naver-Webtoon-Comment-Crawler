# Naver-Webtoon-Comment-Crawler

# 개요 
- 크롤링할 사이트 : 네이버웹툰 (https://comic.naver.com)
- 목표 : 
    1. 모든 웹툰의 titleId을 포함한 웹툰 연재 정보 저장
    2. 웹툰 별 회차별로 접근하여 댓글 크롤링 후 저장  
- 크롤링 방법 : selenium 라이브러리를 이용하여 XPath와 CSS_SELECTOR 방법으로 WebElement에 접근하여 데이터 추출함

<br><br>

<!-- 
# 상세 정보
## 📌 1. 요일별 웹툰 조회 
아래는 요일별로 인기순 정렬하는 URL이다. (월-일)  
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=mon
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=tue
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=wed
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=thu
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=fri
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=sat
https://m.comic.naver.com/webtoon/weekday?sort=ALL_READER&week=sun

<!-- 
### ✅ sort 옵션 
- `ALL_READER` 인기순 (디폴트)
- `FEMALE_READER` 여성 인기순
- `MALE_READER` 남성 인기순
- `HIT` 조회순
- `UPDATE` 업데이트순

<br>

## 📌 2. 웹툰 별 상세페이지 URL
https://m.comic.naver.com/webtoon/list?titleId=807831&week=mon 혹은
https://m.comic.naver.com/webtoon/list?titleId=807831 와 같이 파라미터 titleId로 접근가능함

<br>

### ✅ 웹툰 상세 페이지에서 얻을 수 있는 정보 (예시)
- title_id : 796152
- title : 마루는 강쥐
- summary : 어린이가 되어버린 강아지 마루!
- author : 모죠
- score : 9.98
- count_num : 10만
- genre : 에피소드
- genre_detail : 개그
- week_days : ['화']
- episode_count : 50 -->
