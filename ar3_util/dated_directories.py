from pathlib import Path, PosixPath, WindowsPath

import datetime
import json
from typing import List, Dict


class ComplexEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, PosixPath):
      return str(obj)
    if isinstance(obj, WindowsPath):
      return str(obj)
    if isinstance(obj, datetime.datetime):
      return obj.isoformat()
    if isinstance(obj, datetime.date):
      return obj.isoformat()
    return json.JSONEncoder.default(self, obj)


class DatedDirectories:
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
      with open(dirinfofile, 'r') as f:
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
    with open(dirinfofile, 'w') as f:
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

    with open(Path(path_to_create / DatedDirectories.DIRINFO_FILENAME), 'w') as f:
      json.dump(dirinfo, f, indent=2)

    return path_to_create



  @staticmethod
  def dated_dir_is_closed(pathname:Path) -> bool:
    control_filename = pathname / DatedDirectories.DIRINFO_FILENAME
    if not control_filename.is_file():
      raise RuntimeError(f'Expected DateDirectory control file in {pathname}')
    with open(control_filename, 'r') as f:
      controldata = json.load(f)
    return controldata['is_complete']

  @staticmethod
  def set_dir_to_open(pathname:Path, comment:str) -> None:
    control_filename = pathname / DatedDirectories.DIRINFO_FILENAME
    if DatedDirectories.is_dated_dir(pathname):
      with open(control_filename, 'r') as f:
        controldata = json.load(f)
      controldata['is_complete'] = False
      controldata['comment'] = comment
    else:
      controldata = {
        'info': 'This is a managed Data Directory',
        'created_date': datetime.datetime.now().isoformat(),
        'comment':comment,
        'is_complete': False
      }
    with open(control_filename, 'w') as f:
      json.dump(controldata, f, indent=2, cls=ComplexEncoder)

  @staticmethod
  def is_dated_dir(pathname:Path) -> bool:
    control_filename = pathname / DatedDirectories.DIRINFO_FILENAME
    is_dd=False
    if control_filename.is_file():
      is_dd=True
    return is_dd

  @staticmethod
  def is_dated_dir_and_closed(pathname:Path) -> bool:
    if not DatedDirectories.is_dated_dir(pathname):
      return False
    if not DatedDirectories.dated_dir_is_closed(pathname):
      return False
    return True


