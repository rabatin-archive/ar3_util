

import json
import pickle
import sqlite3
from pathlib import Path

class KeyDB:

  @staticmethod
  def create_new_db(filename: Path):
    con = sqlite3.connect(filename)
    cur = con.cursor()
    cur.execute('''CREATE TABLE DATA(record_key TEXT UNIQUE, record_value BLOB)''')
    con.commit()
    con.close

  def __init__(self, filename: Path, auto_commit:bool):
    self.filename = filename
    self.con = None
    self.commitonclose=False
    self.auto_commit = auto_commit

  def __enter__(self):
    if not self.filename.is_file():
      self.filename.parent.mkdir(parents=True, exist_ok=True)
      KeyDB.create_new_db(self.filename)
    if not self.filename.is_file():
      raise RuntimeError(f'Failed to create file of name {self.filename}')
    self.open()
    return self


  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.close()

  def open(self):
    if self.con is None:
      self.con = sqlite3.connect(self.filename)
    else:
      raise RuntimeError(f'Database already open: {self.filename}')

  def close(self):
    if self.commitonclose:
      self.con.commit()
    if self.con:
      self.con.close()
      self.con = None

  def store(self, key: str, value):
    if not isinstance(key, str):
      raise RuntimeError(f'Key must be of type str, not {type(key)}: {key}')
    cur = self.con.cursor()
    cur.execute('INSERT INTO DATA VALUES (?, ?)', (key, value))
    if self.auto_commit:
      self.con.commit()
    else:
      self.commitonclose = True

  def load_all_data(self):
    resultset = {}
    cur = self.con.cursor()
    cur.execute('SELECT record_key, record_value FROM DATA')
    for row in cur:
      resultset[row[0]] = row[1]
    return resultset

  def load_all_keys(self):
    resultset = []
    cur = self.con.cursor()
    cur.execute('SELECT record_key FROM DATA')
    for row in cur:
      resultset.append(row[0])
    return resultset


  def load(self, key:str):
    if not isinstance(key, str):
        raise RuntimeError(f'Key must be of type str, not {type(key)}: {key}')
    cur = self.con.cursor()
    cur.execute('SELECT record_key, record_value FROM DATA WHERE record_key=:r_key', {'r_key': key})
    select_result = cur.fetchone()
    if select_result:
      return {
        select_result[0]:select_result[1]
      }
    else:
      return {}






import uuid

def db_name():
  return Path('db') / Path(f'db_{uuid.uuid4()}.sqlite')

test_data = {
    'a': 100,
    'b': 200,
    'c': 300,
    'info': 'Some Text',
    'info2': 'Some More'
  }


def test0():
  T = db_name()
  with  KeyDB(T, auto_commit=True) as k:
    k.store('a', json.dumps(test_data))
  with  KeyDB(T, auto_commit=True) as k:
    print(k.load_all_data())

def test1():
  T = db_name()
  with KeyDB(T, auto_commit=True) as kdb:
    kdb.store('a', json.dumps(test_data))
    kdb.store('b', pickle.dumps(test_data))
    print(kdb.load_all_data())
    print(kdb.load_all_keys())

def test1a():
  for auto_commit in [True, False]:
    print(auto_commit, flush=True)
    T = db_name()
    with KeyDB(T, auto_commit=auto_commit) as kdb:
      kdb.store('a', json.dumps(test_data))
      kdb.store('b', pickle.dumps(test_data))
      print(kdb.load_all_data())
      print(kdb.load_all_keys())


def tests():
  test0()
  test1()
  test1a()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
  tests()




