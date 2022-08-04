

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


