from pathlib import Path
import datetime
import json


class DatedDirectories:
  DIRINFO_FILENAME = '__dirinfo__.json'

  def __init__(self, rootpath: Path, create_if_not_exist: bool = True):
    self.rootpath = rootpath
    if create_if_not_exist:
      self.rootpath.mkdir(parents=True, exist_ok=True)
    if not self.rootpath.is_dir():
      raise RuntimeError(f'Not a valid directory: {self.rootpath}')

  @staticmethod
  def dated_to_string(dt: datetime.datetime):
    return dt.now().isoformat(sep='_').replace(':', 'x').replace('.', 'X')

  @staticmethod
  def string_to_datetime(datetimestring: str):
    return datetime.datetime.fromisoformat(datetimestring[3:].replace('x', ':').replace('X', '.'))

  def get_paths(self):
    paths = []
    for d in self.rootpath.iterdir():
      if d.is_dir():
        if d.name.startswith('DD_'):
          paths.append(d)
    return paths

  def get_newest(self):
    paths = {}
    cnt = 0
    for d in self.rootpath.iterdir():
      if d.is_dir():
        if d.name.startswith('DD_'):
          cnt += 1
          paths[DatedDirectories.string_to_datetime(d.name)] = d
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
  def close_datadir(datapath: Path):
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

  def create_dated(self, use_datetime: datetime.datetime = None):
    if not use_datetime:
      use_datetime = datetime.datetime.now()
    pathname = 'DD_' + DatedDirectories.dated_to_string(use_datetime)
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
