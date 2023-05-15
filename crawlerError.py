from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config.save_path import ERROR_BEST_COMMENTS_TXT_FILE
from config.slack_credential import SLACK_API_TOKEN, CHANNEL_NAME

class CrawlerError(Exception):
    def __init__(self, message, title_id=None, epi_no=None):
        super().__init__(message)
        self.title_id = title_id
        self.epi_no = epi_no
        self.log_error()
        self.send_slack_notification()


    def log_error(self):
        with open(ERROR_BEST_COMMENTS_TXT_FILE, 'a') as f:
            f.write(f"{self}\n")


    def __str__(self):
        return f"{self.title_id}/{self.epi_no}"


    def send_slack_notification(self):
        client = WebClient(token=SLACK_API_TOKEN)
        try:
            response = client.chat_postMessage(
                channel=CHANNEL_NAME,
                text=f"CrawlerError occurred with message-Title ID: {self.title_id} Episode No: {self.epi_no} \n{super().__str__()}"
            )
            print(f"Slack Notification Sent: {response['ts']}")
        except SlackApiError as e:
            print("Slack Notification Failed: ", e.response["error"])