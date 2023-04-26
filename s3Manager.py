import json 
import boto3
from logger import Logger

from config.s3_credential import  AWS_ACCESS_KEY_ID ,AWS_SECRET_ACCESS_KEY, BUCKET_NAME

from config.save_path import *

class S3Manager:
    def __init__(self):
        self.s3 = boto3.resource('s3',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        self.bucket_name = BUCKET_NAME
        self.logger = Logger('s3logger')
        self.logger.set_file_and_stream_handler(S3_LOG_FILE_PATH)


    def save_json_to_s3(self, file_name: str, data): # json 객체 저장 
        try:
            json_data = json.dumps(data).encode('UTF-8')
            response = self.s3.Object(self.bucket_name, file_name).put(Body=json_data)
            self.logger.debug(f"Successfully saved data to {file_name}")
        except Exception as e:
            self.logger.error(f"Error saving data to {file_name}: {e}")

        return response


    def load_json_from_s3(self, file_name: str) :
        try:
            obj = self.s3.Object(self.bucket_name, file_name)
            data = obj.get()['Body'].read().decode('utf-8')
            json_data = json.loads(data)
            self.logger.info(f"Successfully load data to {file_name}")
            return json_data
        except Exception as e:
            self.logger.error(f"Error loading data from {file_name}: {e}")
            return None


#####################원본
# def upload_json_obj_s3(bucket_name, file_name, data): # json 객체 저장 
#     s3 = boto3.resource('s3',
#                     aws_access_key_id=AWS_ACCESS_KEY_ID,
#                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#     # 데이터를 이진 데이터로 직렬화
#     # binary_data = pickle.dumps(data)
#     # print("binary_data : ", binary_data)

#     # 인코딩 
#     json_data = json.dumps(data).encode('UTF-8')
#     # json_data = json.dumps(data)
#     # print("json_data : ", json_data)

#     # S3에 데이터 저장
#     try:
#         # s3.Object(bucket_name, file_name).put(Body=binary_data)
#         s3.Object(bucket_name, file_name).put(Body=json_data)
#         print("저장 완료됨")
#         return True
#     except :
#         return False

# def upload_json_file_s3(bucket, file_name, json_file):  # json 파일 저장 
#     encode_file = bytes(json.dumps(json_file, indent=4).encode('UTF-8'))
#     s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#     try:
#         s3.put_object(Bucket=bucket, Key=file_name, Body=encode_file)
#         return True
#     except:
#         return False
    

# def get_json_obj_s3(bucket_name, file_name) :
#     s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#     response = s3.get_object(Bucket=bucket_name, Key=file_name)
#     data = response['Body'].read().decode('utf-8')
#     json_data = json.loads(data)
#     print(json_data)


# def upload_csv_file_s3(bucket, file_name, csv_file):  # csv 파일 저장 
#     s3 = boto3.client('s3')
#     try:
#         s3.put_object(Bucket=bucket, Key=file_name, Body=csv_file)
#         return True
#     except:
#         return False