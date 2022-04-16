import logging
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').lower()

log_level_map = {
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}


class Logger:

    def __init__(self):

        self._logger = logging.getLogger()
        if self._logger.hasHandlers():
            self._logger.setLevel(level=log_level_map[LOG_LEVEL])
        else:
            logging.basicConfig(level=log_level_map[LOG_LEVEL])

    @property
    def getlogger(self):
        return self._logger
