import os
import logging
import re
from logging.handlers import TimedRotatingFileHandler
import sys


class Logger(logging.Logger):
    def __init__(self, name="Base", sub_name="Server"):
        super(Logger, self).__init__(name=name, level=logging.INFO)
        self.name = name
        self.sub_name = sub_name
        self.__log_path__ = './logs/latest.log'
        self.__when__ = "MIDNIGHT"
        self.__time_format__ = "%H:%M:%S"
        if not os.path.isdir("./logs"):
            os.mkdir("./logs")

        self.__logger__format__ = f"[{self.name}][{self.sub_name}][%(asctime)s][%(threadName)s/%(levelname)s]: %(message)s"

        file_handler = TimedRotatingFileHandler(filename=self.__log_path__, when=self.__when__,
                                                interval=1, backupCount=30)
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
        file_handler.setFormatter(logging.Formatter(self.__logger__format__))
        self.addHandler(file_handler)

        self.__level_filter()
        self.__set_logger()

    def __level_filter(self):
        self.info_filter = logging.Filter()
        self.info_filter.filter = lambda record: record.levelno == logging.INFO
        self.err_filter = logging.Filter()
        self.err_filter.filter = lambda record: record.levelno > logging.WARNING
        self.warn_filter = logging.Filter()
        self.warn_filter.filter = lambda record: record.levelno == logging.WARNING
        self.debug_filter = logging.Filter()
        self.debug_filter.filter = lambda record: record.levelno == logging.DEBUG

    def __set_logger(self):
        self.__logger__format__ = f"\033[36m[\033[32m{self.name}\033[36m][\033[33m{self.sub_name}\033[36m]" \
                                  f"[\033[32m%(asctime)s\033[36m]" \
                                  "[\033[32m%(threadName)s\033[36m/\033[32m%(levelname)s\033[36m]: " \
                                  "\033[0m%(message)s\033[0m"
        info_sh = logging.StreamHandler(sys.stdout)
        info_sh.setFormatter(logging.Formatter(self.__logger__format__, self.__time_format__))
        info_sh.addFilter(self.info_filter)
        self.addHandler(info_sh)

        self.__logger__format__ = f"\033[36m[\033[32m{self.name}\033[36m][\033[33m{self.sub_name}\033[36m]" \
                                  f"[\033[33m%(asctime)s\033[36m]" \
                                  "[\033[33m%(threadName)s\033[36m/\033[33m%(levelname)s\033[36m]: " \
                                  "\033[33m%(message)s\033[0m"
        warn_sh = logging.StreamHandler(sys.stdout)
        warn_sh.setFormatter(logging.Formatter(self.__logger__format__, self.__time_format__))
        warn_sh.addFilter(self.warn_filter)
        self.addHandler(warn_sh)

        self.__logger__format__ = f"\033[36m[\033[32m{self.name}\033[36m][\033[33m{self.sub_name}\033[36m]" \
                                  f"[\033[31m%(asctime)s\033[36m]" \
                                  "[\033[31m%(threadName)s\033[36m/\033[31m%(levelname)s\033[36m]: " \
                                  "\033[31m%(message)s\033[0m"
        err_sh = logging.StreamHandler(sys.stdout)
        err_sh.setFormatter(logging.Formatter(self.__logger__format__, self.__time_format__))
        err_sh.addFilter(self.err_filter)
        self.addHandler(err_sh)

        self.__logger__format__ = f"\033[36m[\033[32m{self.name}\033[36m][\033[33m{self.sub_name}\033[36m]" \
                                  f"[\033[34m%(asctime)s\033[36m]" \
                                  "[\033[34m%(threadName)s\033[36m/\033[34m%(levelname)s\033[36m]: " \
                                  "\033[34m%(message)s\033[0m"
        debug_sh = logging.StreamHandler(sys.stdout)
        debug_sh.setFormatter(logging.Formatter(self.__logger__format__, self.__time_format__))
        debug_sh.addFilter(self.debug_filter)
        self.addHandler(debug_sh)

    def setDebug(self, debug=False):
        if debug:
            self.setLevel(logging.DEBUG)
        else:
            self.setLevel(logging.INFO)


if __name__ == '__main__':
    a = Logger("BLH", "[房间号]")
    a.setDebug(True)
    a.debug("Test")
    a.info("Test")
    a.warning("Test")
    a.error("Test")
    a.critical("Test")
