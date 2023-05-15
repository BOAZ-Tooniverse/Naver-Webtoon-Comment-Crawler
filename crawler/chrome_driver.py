import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from config.save_path import CHROME_DRIVER_LOG_FILE
from logger.crawler_logger import CrawlerLogger


class ChromeDriver:


    def __init__(self):
        """
        Create a ChromeDriver instance
        """
        self.logger = CrawlerLogger('chromedriver', logging.DEBUG, CHROME_DRIVER_LOG_FILE)
        self.service = None
        self.driver = None

    def start(self):
        """
        Execute ChromeDriver
        """
        try:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299"
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ["enable-logging"])
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('user-agent=' + user_agent)
            self.service = Service(ChromeDriverManager().install())
            self.service.start()
            self.driver = webdriver.Chrome(service=self.service, options=options)
        except WebDriverException as e:
            self.logger.error(f"Failed to create ChromeDriver: {str(e)}")
            self.driver = None
            self.service = None
        return self.driver

    def __del__(self):
        if self.driver:
            self.driver.quit()
        if self.service:
            self.service.stop()

    def stop(self):
        """
        Stop ChromeDriver
        """
        if self.driver:
            self.driver.quit()
        if self.service:
            self.service.stop()

    def get_driver(self):
        """
        Return driver
        """
        return self.driver