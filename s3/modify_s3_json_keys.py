import boto3
import json
import copy
from crawler.weekly_tooninfo_crawler import *
from config.s3_credential import  AWS_ACCESS_KEY_ID ,AWS_SECRET_ACCESS_KEY, BUCKET_NAME

def modify_s3_json_keys() :
    # AWS 계정 자격 증명 정보 설정
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    # S3 클라이언트 생성
    s3_client = session.client('s3')

    # S3 버킷의 폴더 정보 가져오기
    prefix = ''
    folders = []
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')
    for obj in response.get('CommonPrefixes', []):
        folder_name = obj['Prefix'].strip('/')
        if folder_name != 'test' : 
            folders.append(folder_name)

    for folder in folders :  
        # # S3 버킷 내의 모든 JSON 파일에 대해 처리
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder)
        for obj in response['Contents']:
            file_key = obj['Key']
            print("\n!------- file_key :", file_key)
            if file_key.endswith('.json'):  # JSON 파일인 경우에만 처리
                # JSON 파일 내용 읽기
                file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
                file_content = file_obj['Body'].read().decode('utf-8')
                json_data = json.loads(file_content)
                
                # 키 값을 변경하는 작업 수행
                keys_to_remove = []
                keys_to_add = {}
                for key, value in json_data.items():
                    if value != '{}':  # 비어있지 않은 경우에만 키 값을 변경
                        if "commentNo:'" in key:
                            new_key = key.split("'")[1] 
                            keys_to_remove.append(key)
                            keys_to_add[new_key] = copy.deepcopy(value)

                # 변경된 키를 제거하고 새 키를 추가
                for key in keys_to_remove:
                    json_data.pop(key)
                json_data.update(keys_to_add)
                
                # 변경된 JSON 데이터를 S3에 다시 저장
                new_file_content = json.dumps(json_data)
                s3_client.put_object(Body=new_file_content, Bucket=BUCKET_NAME, Key=file_key)

def modify_s3_json_schema(end_title_id : int) :
    tooninfo_crawler = WeeklyToonInfoCrawler()
    total_toon_info_df = tooninfo_crawler.load_total_tooninfo()
    title_id_list = total_toon_info_df["title_id"].values.tolist()
    end_idx = title_id_list.index(end_title_id)

    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )

    s3_client = session.client('s3')

    for i in range(0,end_idx+1):
        folder = str(title_id_list[i])
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder)
        # 파일 하나씩 가져옴
        for obj in response['Contents']: 
            file_key = obj['Key']
            if file_key.endswith('.json'): 
                file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
                file_content = file_obj['Body'].read().decode('utf-8')
                json_data = json.loads(file_content)
                result = []
                # 스키마 변경
                for key, value in json_data.items():
                    if value != '{}': 
                        result.append({'comment_id': key, **value})
                # save
                new_file_content = json.dumps(result)
                s3_client.put_object(Body=new_file_content, Bucket=BUCKET_NAME, Key=file_key)