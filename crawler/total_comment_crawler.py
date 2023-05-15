# class TotalCommentCrawler :

    
#     def get_total_comments(driver, title_id_list, epi_cnt_list) : # 전체 댓글 수집

#         for title_id, epi_cnt in zip(title_id_list, epi_cnt_list): 
#             print(title_id, epi_cnt)

#             # 한 웹툰 -> 여러 회차 정보 불러오기
#             for epi_no in range(1, epi_cnt + 1) :
#                 title_id_list = [] 
#                 epi_no_list = []
#                 comments_list = []
#                 nickname_list = []
#                 login_id_list = []
#                 reply_cnt_list = []
#                 recomm_cnt_list = []
#                 unrecomm_cnt_list = []
#                 write_date_list = []
#                 save_date_list = []
#                 isbest_list = []

#                 if epi_no == 6 : #Test용
#                     break
#                 episode_url = 'https://comic.naver.com/webtoon/detail?titleId=' + str(title_id) + '&no=' + str(epi_no)
#                 driver.get(episode_url)

#                 # 총 댓글 갯수
#                 # comments_num = driver.find_element(by=By.CSS_SELECTOR, value='#cbox_module > div > div.u_cbox_head > span').text
#                 # print(f'comments_num : {comments_num}')

#                 # # BEST 댓글 정보 가져오기
#                 list_comment = driver.find_elements(by=By.CSS_SELECTOR, value='#cbox_module_wai_u_cbox_content_wrap_tabpanel > ul > li')
#                 for item in list_comment : 
#                     # print("item : " ,  item)

#                     comment = item.find_element(by=By.CLASS_NAME, value='u_cbox_contents').text
#                     nickname  = item.find_element(by=By.CLASS_NAME, value='u_cbox_nick').text
#                     login_id = item.find_element(by=By.CLASS_NAME, value='u_cbox_id').text[1:-1]
#                     reply_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_reply_cnt').text
#                     recomm_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_cnt_recomm').text
#                     unrecomm_cnt = item.find_element(by=By.CLASS_NAME, value='u_cbox_cnt_unrecomm').text
#                     write_date = item.find_element(by=By.CLASS_NAME, value='u_cbox_date').text
#                     # print(comment)
                    
#                     title_id_list.append(title_id)
#                     epi_no_list.append(epi_no)
#                     comments_list.append(comment)
#                     nickname_list.append(nickname)
#                     login_id_list.append(login_id)
#                     reply_cnt_list.append(reply_cnt)
#                     recomm_cnt_list.append(recomm_cnt)
#                     unrecomm_cnt_list.append(unrecomm_cnt)
#                     write_date_list.append(write_date)
#                     save_date_list.append(datetime.now())
#                     isbest_list.append(True)

#                 epi_best_comments = {"title_id" : title_id_list,"epi_no" : epi_no_list,"comment" : comments_list,"nickname" : nickname_list,"login_id" : login_id_list,"reply_cnt" : reply_cnt_list ,"recomm_cnt" : recomm_cnt_list,"unrecomm_cnt" : unrecomm_cnt_list ,"write_date" : write_date_list,"save_date" : save_date_list,"is_best" :isbest_list}
#                 df = pd.DataFrame(epi_best_comments)
#                 print(df.head(5))
#                 file_name = str(title_id)+ '_' + str(epi_no) + '.csv'
#                 df.to_csv(file_name, encoding = "utf-8-sig")
#                 # print("epi_best_comments :", epi_best_comments)

#                 time.sleep(1)