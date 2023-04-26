import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.slack_credential import SLACK_API_TOKEN, CHANNEL_NAME_INFO

class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.logger = logging.getLogger(name)
        self.name = name
        self.client = WebClient(token=SLACK_API_TOKEN)

    def set_file_and_stream_handler(self, file_path) : 
        fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
        fileHandler = logging.FileHandler(file_path)
        streamHandler = logging.StreamHandler()
        
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(streamHandler)
        self.logger.setLevel(logging.DEBUG)
        fileHandler.setFormatter(fomatter)
        streamHandler.setFormatter(fomatter)
        
        self.logger.info(f'Complete to set {self.name}')
        return self.logger
    
    def info(self, msg, *args, **kwargs):
        # 새로운 로그 레벨을 추가하고자 할 때는 levelno를 지정하면 됩니다.
        if self.isEnabledFor(logging.INFO):
            self._log(logging.INFO, msg, args, **kwargs)
        
        try:
            response = self.client.chat_postMessage(
                channel=CHANNEL_NAME_INFO,
                text=msg
            )
            print(f"Slack Notification Sent: {response['ts']}")
        except SlackApiError as e:
            print("Slack Notification Failed: ", e.response["error"])