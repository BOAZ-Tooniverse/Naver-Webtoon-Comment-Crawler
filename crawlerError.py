from config.save_path import ERROR_BEST_COMMENTS_TXT_FILE

class CrawlerError(Exception):
    def __init__(self, message, title_id=None, epi_no=None):
        super().__init__(message)
        self.title_id = title_id
        self.epi_no = epi_no
        self.log_error()

    def log_error(self):
        with open(ERROR_BEST_COMMENTS_TXT_FILE, 'a') as f:
            f.write(f"{self}\n")

    def __str__(self):
        return f"{self.title_id}/{self.epi_no}"