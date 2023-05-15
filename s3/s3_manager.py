import json 
import boto3
import logging
from config.s3_credential import  AWS_ACCESS_KEY_ID ,AWS_SECRET_ACCESS_KEY, BUCKET_NAME
from logger.crawler_logger import CrawlerLogger
from config.save_path import *


class S3Manager:

    
    def __init__(self):
        self.s3 = boto3.resource('s3',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        self.bucket_name = BUCKET_NAME
        self.logger = CrawlerLogger('s3logger',logging.INFO, S3_LOG_FILE_PATH)

    def save_json_to_s3(self, file_name: str, data): 
        """
        json 객체를 s3에 저장 
        """
        try:
            json_data = json.dumps(data).encode('UTF-8')
            response = self.s3.Object(self.bucket_name, file_name).put(Body=json_data)
            self.logger.debug(f"Successfully saved data to {file_name}")
        except Exception as e:
            self.logger.error(f"Error saving data to {file_name}: {e}")

        return response

    def load_json_from_s3(self, file_name: str) :
        """
        json 객체를 s3에서 불러옴
        """
        try:
            obj = self.s3.Object(self.bucket_name, file_name)
            data = obj.get()['Body'].read().decode('utf-8')
            json_data = json.loads(data)
            self.logger.info(f"Successfully load data to {file_name}")
            return json_data
        except Exception as e:
            self.logger.error(f"Error loading data from {file_name}: {e}")
            return None