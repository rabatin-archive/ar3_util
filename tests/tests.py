import datetime
import random
import pickle
import json
import unittest
import uuid
from pathlib  import Path
from ar3_util.toml_parser import TOMLParser
import logging
from ar3_util.standard_logger import logging_level_string_to_level, apply_logger_handler
from ar3_util.keydb import KeyDB
from ar3_util.dated_directories import DatedDirectories
# from tempfile import gettempdir

TMP_PATH = Path('__tmp__')


class KeyDBTestCase(unittest.TestCase):

  def setUp(self):
    TMP_PATH.mkdir(exist_ok=True)

  @staticmethod
  def db_name():
    return TMP_PATH / Path(f'db_{uuid.uuid4()}.sqlite')

  test_data = {
    'a': 100,
    'b': 200,
    'c': 300,
    'info': 'Some Text',
    'info2': 'Some More'
  }

  def test_test1a(self):
    for auto_commit in [True, False]:
      T = KeyDBTestCase.db_name()
      with KeyDB(T, auto_commit=auto_commit) as kdb:
        kdb.store('a', json.dumps(KeyDBTestCase.test_data))
        kdb.store('b', pickle.dumps(KeyDBTestCase.test_data))
        data = kdb.load_all_data()
        datavalue_a = json.loads(data['a'])
        datavalue_b = pickle.loads(data['b'])
        self.assertDictEqual(KeyDBTestCase.test_data, datavalue_a)
        self.assertDictEqual(KeyDBTestCase.test_data, datavalue_b)

class DatedDirTester(unittest.TestCase):

  def setUp(self):
    TMP_PATH.mkdir(exist_ok=True)

  def test0(self):
    nw = datetime.datetime.now()
    s = DatedDirectories.datetime_to_pathname(nw)
    self.assertEqual(nw, DatedDirectories.pathname_extract_datetime(s))

  def test_creationfunctions(self):
    testroot = TMP_PATH / str(uuid.uuid4())
    testroot.mkdir(parents=True,exist_ok=False)
    nw = datetime.datetime.now()
    dd = DatedDirectories(testroot)
    createdpath = dd.create_dated(nw)
    self.assertTrue(DatedDirectories.is_dated_dir(createdpath))
    newest = dd.get_newest()
    self.assertEqual(newest['path_count'], 1)
    self.assertEqual(newest['newest_path'], createdpath)
    self.assertEqual(newest['newest_timestamp'], DatedDirectories.pathname_extract_datetime(str(createdpath.name)))
    self.assertTrue(DatedDirectories.is_dated_dir(createdpath))
    self.assertFalse(DatedDirectories.is_dated_dir_and_closed(createdpath))
    self.assertFalse(DatedDirectories.dated_dir_is_closed(createdpath))
    self.assertRaises(RuntimeError, DatedDirectories.dated_dir_is_closed, testroot)
    DatedDirectories.close_datadir(createdpath)
    self.assertTrue(DatedDirectories.dated_dir_is_closed(createdpath))
    DatedDirectories.set_dir_to_open(createdpath, 'test')
    self.assertFalse(DatedDirectories.dated_dir_is_closed(createdpath))
    DatedDirectories.close_datadir(createdpath)
    self.assertTrue(DatedDirectories.dated_dir_is_closed(createdpath))

  def test_loadingsortedlist(self):
    testroot = TMP_PATH / str(uuid.uuid4())
    testroot.mkdir(parents=True, exist_ok=False)
    dd = DatedDirectories(testroot)
    timestamps = []
    for i in range(1, 101):
      timestamps.append(
        datetime.datetime(year=2022,month=6,day=1,hour=10,minute=1, second=1, microsecond=i)
      )
    rand_timestamps = random.sample(timestamps, len(timestamps))
    for ts in rand_timestamps:
      DatedDirectories.close_datadir(dd.create_dated(use_datetime=ts))
    pathlist = dd.get_paths()
    timestamplist = []
    for x in pathlist:
      timestamplist.append(DatedDirectories.pathname_extract_datetime(str(x.name)))
    self.assertEqual(timestamps, timestamplist)


class TOMLParserTest(unittest.TestCase):

  TESTTOML = Path('data/merkur_global_config.toml')

  def setUp(self):
    TMP_PATH.mkdir(exist_ok=True)

  def test_parsing(self):
    tmlfle = TOMLParser(TOMLParserTest.TESTTOML)
    s = tmlfle.dumps()
    with open('__tmp__/s.toml', 'w') as f:
      f.write(s)
    tmlfle.dump(Path('__tmp__/ss.toml'), exist_ok=True)
    with open('__tmp__/s.toml', 'r') as f:
      rl = f.readlines()
    for l in rl:
      self.assertFalse(TOMLParser.DROPBOX_MARKER in l)
      self.assertFalse(TOMLParser.LEFT_MARKER in l)
      self.assertFalse(TOMLParser.RIGHT_MARKER in l)


class StandardLogger(unittest.TestCase):

  def setUp(self):
    TMP_PATH.mkdir(exist_ok=True)

  def test_logging_level_string_to_level(self):
    self.assertEqual(logging_level_string_to_level('DEBUG'), logging.DEBUG)
    self.assertRaises(ValueError, logging_level_string_to_level, 'failDEBUG')

  def test_log(self):
    logifle = Path('__tmp__/__ar3util__test__.log')
    s = str(uuid.uuid4())
    loggername = f'__{s}__'
    if logifle.is_file():
      logifle.unlink()
    apply_logger_handler(screenoutput=False, logger_name=loggername, logfilename= str(logifle), logging_level = logging.DEBUG)
    testlog = logging.getLogger(loggername + '.TEST')
    testlog.debug(s)
    comp = f'[DEBUG:{loggername}.TEST] {s}'
    with open(logifle, 'r') as f:
      rl = f.readlines()
    self.assertTrue(comp in rl[0])



if __name__ == '__main__':
  unittest.main()
