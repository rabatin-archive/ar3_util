# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

"""
Provides standardised logger format creation with file rotation where available by the OS
"""


import logging.handlers
import sys
from ar3_util.os_detector import is_linux, is_windows, os_name

def logging_level_string_to_level(logging_level_as_str:str):
  name_to_level = {
    'CRITICAL': logging.CRITICAL,
    'FATAL': logging.FATAL,
    'ERROR': logging.ERROR,
    'WARN': logging.WARNING,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    'NOTSET': logging.NOTSET
  }
  if logging_level_as_str not in name_to_level:
    raise ValueError(f'Invalid logging level code: {logging_level_as_str}')
  return name_to_level[logging_level_as_str]


def apply_logger_handler(screenoutput:bool, logger_name:str, logfilename:str, logging_level:int = logging.DEBUG):
  logger = logging.getLogger(logger_name)
  logger.setLevel(logging_level)

  fulllogfilename = logfilename

  if is_windows():
    filehandler = logging.FileHandler(fulllogfilename, mode='w')
  elif is_linux():
    filehandler = logging.handlers. \
      RotatingFileHandler(filename=fulllogfilename,
                          mode='a',
                          maxBytes=300 * 1024 * 1024,
                          backupCount=100)
  else:
    raise RuntimeError(f'Unknown OS {os_name()}')
  generalformatter = logging.Formatter(
    '%(asctime)s [%(levelname)s:%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  filehandler.setFormatter(generalformatter)
  logger.addHandler(filehandler)

  if screenoutput:
    screenhandler = logging.StreamHandler(sys.stdout)
    screenhandler.setFormatter(generalformatter)
    logger.addHandler(screenhandler)
