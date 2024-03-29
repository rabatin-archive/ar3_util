# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

"""
Provides a easy way to create unique directories with embedded timestamps and indicator files if the processes
writing to the path have been successfully completed or not
"""

from pathlib import Path, PosixPath, WindowsPath

import datetime
import json
from typing import List, Dict


class DatedDirectories:
  """
  Provides a easy way to create unique directories with embedded timestamps and indicator files if the processes
  writing to the path have been successfully completed or not
  Key Features:
   - Directory names have an embedded timestamp and can be sorted for example to find the latest
   - Directories have a control file that can be used to indicate if a process writing to the directory has
     successfully completed or not
  Use cases:
  - Regular downloads where each download needs to be in a distinct directory and it needs to be ordered by date/times
    to identify the latest and/or the general order of download
  - Any ad-hoc processes that need to create unique paths to store results, but where a random ID is not practical
  - Any process that can fail and where there has to be a marker if the process was successful
  """
  class ComplexEncoder(json.JSONEncoder):
    """
    Helper class to read/write JSON formatted control files
    """
    def default(self, o):
      if isinstance(o, PosixPath):
        return str(o)
      if isinstance(o, WindowsPath):
        return str(o)
      if isinstance(o, datetime.datetime):
        return o.isoformat()
      if isinstance(o, datetime.date):
        return o.isoformat()
      return json.JSONEncoder.default(self, o)

  DIRINFO_FILENAME = '__dirinfo__.json'

  def __init__(self, rootpath: Path, create_if_not_exist: bool = True):
    self.rootpath = rootpath
    if create_if_not_exist:
      self.rootpath.mkdir(parents=True, exist_ok=True)
    if not self.rootpath.is_dir():
      raise RuntimeError(f'Not a valid directory: {self.rootpath}')

  @staticmethod
  def datetime_to_pathname(dt: datetime.datetime) -> str:
    return 'DD_' + dt.isoformat(sep='_').replace(':', 'x').replace('.', 'X')

  @staticmethod
  def pathname_extract_datetime(datetimestring: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(datetimestring[3:].replace('x', ':').replace('X', '.'))

  def get_paths(self) -> List[Path]:
    paths = []
    for d in self.rootpath.iterdir():
      if d.is_dir():
        if d.name.startswith('DD_'):
          paths.append(d)
    paths.sort(key=lambda x: DatedDirectories.pathname_extract_datetime(str(x.name)))
    return paths

  def get_newest(self) -> Dict:
    paths = {}
    cnt = 0
    for d in self.rootpath.iterdir():
      if d.is_dir():
        if d.name.startswith('DD_'):
          cnt += 1
          paths[DatedDirectories.pathname_extract_datetime(d.name)] = d
    if len(paths) == 0:
      return {
        'path_count': 0
      }
    latest = max(paths.keys())
    return {
      'path_count': cnt,
      'newest_timestamp': latest,
      'newest_path': paths[latest]
    }

  @staticmethod
  def close_datadir(datapath: Path) -> None:
    dirinfofile = Path(datapath) / DatedDirectories.DIRINFO_FILENAME
    if dirinfofile.is_file():
      with open(dirinfofile, 'r', encoding='utf-8') as f:
        dirinfo = json.load(f)
    else:
      dirinfo = {
        'info': 'This is a managed Data Directory',
        'comment': 'There was no create event for this path. Ignore the create Timestamp.',
        'created_date': datetime.datetime.now().isoformat(),
        'is_complete': False
      }
    dirinfo['is_complete'] = True
    dirinfo['completed_date']: datetime.datetime.now().isoformat()
    with open(dirinfofile, 'w', encoding='utf-8') as f:
      json.dump(dirinfo, f, indent=2)

  def create_dated(self, use_datetime: datetime.datetime = None) -> Path:
    if not use_datetime:
      use_datetime = datetime.datetime.now()
    pathname = DatedDirectories.datetime_to_pathname(use_datetime)
    path_to_create = self.rootpath / pathname
    path_to_create.mkdir(parents=False, exist_ok=False)

    dirinfo = {
      'info': 'This is a managed Data Directory',
      'created_date': datetime.datetime.now().isoformat(),
      'is_complete': False
    }

    with open(Path(path_to_create / DatedDirectories.DIRINFO_FILENAME), 'w', encoding='utf-8') as f:
      json.dump(dirinfo, f, indent=2)

    return path_to_create

  @staticmethod
  def dated_dir_is_closed(pathname: Path) -> bool:
    control_filename = pathname / DatedDirectories.DIRINFO_FILENAME
    if not control_filename.is_file():
      raise RuntimeError(f'Expected DateDirectory control file in {pathname}')
    with open(control_filename, 'r', encoding='utf-8') as f:
      controldata = json.load(f)
    return controldata['is_complete']

  @staticmethod
  def set_dir_to_open(pathname: Path, comment: str) -> None:
    control_filename = pathname / DatedDirectories.DIRINFO_FILENAME
    if DatedDirectories.is_dated_dir(pathname):
      with open(control_filename, 'r', encoding='utf-8') as f:
        controldata = json.load(f)
      controldata['is_complete'] = False
      controldata['comment'] = comment
    else:
      controldata = {
        'info': 'This is a managed Data Directory',
        'created_date': datetime.datetime.now().isoformat(),
        'comment': comment,
        'is_complete': False
      }
    with open(control_filename, 'w', encoding='utf-8') as f:
      json.dump(controldata, f, indent=2, cls=DatedDirectories.ComplexEncoder)

  @staticmethod
  def is_dated_dir(pathname: Path) -> bool:
    control_filename = pathname / DatedDirectories.DIRINFO_FILENAME
    is_dd = False
    if control_filename.is_file():
      is_dd = True
    return is_dd

  @staticmethod
  def is_dated_dir_and_closed(pathname: Path) -> bool:
    if not DatedDirectories.is_dated_dir(pathname):
      return False
    if not DatedDirectories.dated_dir_is_closed(pathname):
      return False
    return True
