import time

import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

# format the log entries
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

handler = TimedRotatingFileHandler('D:\\git\Parallel-fdc\\logs\\fdc_manager\\testRotation.log', 
                                   when= 'D', atTime= datetime.datetime(2020, 5, 17, 10, 8) , #'midnight',
                                   backupCount=10)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# generate example messages
for i in range(10000):
    time.sleep(1)
    logger.debug('debug message')
    logger.info('informational message')
    logger.warn('warning')
    logger.error('error message')
    logger.critical('critical failure')