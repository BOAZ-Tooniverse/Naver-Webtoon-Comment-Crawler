import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config.slack_credential import SLACK_API_TOKEN, CHANNEL_NAME_INFO



class CrawlerLogger(logging.Logger):


    def __init__(self, name, level=logging.INFO, log_file=None):
        super().__init__(name)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(formatter)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.logger.addHandler(stream_handler)
        self.client = WebClient(token=SLACK_API_TOKEN)

    def info(self, msg, *args, **kwargs):
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