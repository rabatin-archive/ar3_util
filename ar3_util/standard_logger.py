
import logging.handlers
import platform
import sys

def logging_level_string_to_level(logging_level_as_str:str):
  nameToLevel = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
  }
  if logging_level_as_str not in nameToLevel:
    raise ValueError(f'Invalid logging level code: {logging_level_as_str}')
  return nameToLevel[logging_level_as_str]


def apply_logger_handler(screenoutput:bool, logger_name:str, logfilename:str, logging_level:int = logging.DEBUG):
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging_level)

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
