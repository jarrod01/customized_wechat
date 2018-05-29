import os, logging
from logging.handlers import TimedRotatingFileHandler

fh = TimedRotatingFileHandler('test_log', encoding='utf-8', when='d', interval=1, backupCount=7)
fmt = '%(asctime)s\t%(name)s\t%(levelname)s:\t%(message)s'
# datefmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(fmt)
fh.setFormatter(formatter)

logger_name = 'test_log'
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO)
logger.addHandler(fh)
# logging.basicConfig(handlers=[fh,console], level=logging.DEBUG)

logger.debug('这是debug')
logger.info('这是info')
logger.warning('这是warning')
logger.error('这是error')
logger.critical('这是critical')

