
import logging.handlers
import platform
import sys

def apply_logger_handler(screenoutput:bool, logger_name:str, logfilename:str):
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging.DEBUG)

  fulllogfilename = logfilename

  if platform.system() == 'Windows':
    filehandler = logging.FileHandler(fulllogfilename, mode='w')
  else:
    filehandler = logging.handlers. \
      RotatingFileHandler(filename=fulllogfilename,
                          mode='a',
                          maxBytes=300 * 1024 * 1024,
                          backupCount=100)
  generalformatter = logging.Formatter(
    '%(asctime)s [%(levelname)s:%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  filehandler.setFormatter(generalformatter)
  logger.addHandler(filehandler)

  if screenoutput:
    screenhandler = logging.StreamHandler(sys.stdout)
    screenhandler.setFormatter(generalformatter)
    logger.addHandler(screenhandler)
