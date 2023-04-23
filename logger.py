import logging

class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.logger = logging.getLogger(name)
        self.name = name

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

    