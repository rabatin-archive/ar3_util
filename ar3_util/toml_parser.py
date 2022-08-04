from pathlib import Path
import os
import toml
import json
import platform
from ar3_util.os_detector import is_linux, is_windows, os_name

class TOMLParser:

  DROPBOX_MARKER = '<#DROPBOX#>'
  LEFT_MARKER = '<?'
  RIGHT_MARKER = '?>'

  def __init__(self, toml_file:Path):
    self.vars = {}
    self.cnt = 0
    with open(toml_file, 'r') as f:
      self.tomldata = toml.load(f)
    self.parsed_dict_cache = None

  @staticmethod
  def _get_windows_dropboox_root() -> Path:
    try:
      json_path = (Path(os.getenv('LOCALAPPDATA')) / 'Dropbox' / 'info.json').resolve()
    except FileNotFoundError:
      json_path = (Path(os.getenv('APPDATA')) / 'Dropbox' / 'info.json').resolve()
    return Path(json_path)

  @staticmethod
  def _find_dropbox_root() -> Path:
    if is_linux():
      dropbox_spectfile = Path('~/.dropbox/info.json').expanduser()
    elif is_windows():
      dropbox_spectfile = TOMLParser._get_windows_dropboox_root()
    else:
      raise RuntimeError(f'Dropbox root config not implemented for OS {os_name()}')
    with open(dropbox_spectfile, 'r') as f:
      dropbox_config = json.load(f)
    return Path(dropbox_config['personal']['path'])

  @staticmethod
  def has_var(s: str) -> bool:
    if TOMLParser.LEFT_MARKER in s and TOMLParser.RIGHT_MARKER in s:
      return True
    else:
      return False

  def parse(self):
    if self.parsed_dict_cache is None:
      self.parsed_dict_cache = self._iterative_parse(self.tomldata)
    return self.parsed_dict_cache

  def dump(self, filename:Path, exist_ok:bool=False):
    if not exist_ok:
      if filename.is_file():
        raise RuntimeError(f'Output file already exists {filename}')
    with open(filename, 'w') as f:
      toml.dump(self.parse(), f)

  def dumps(self):
    return toml.dumps(self.parse())

  def _iterative_parse(self, d_:dict):
    self.cnt = 99
    D= {}
    while self.cnt != 0:
      self.cnt = 0
      D = self._traverse(d_)
    return D

  def _traverse(self, d_:dict):
    d = d_.copy()
    new_dict = {}
    for k, v in d.items():
      if isinstance(v, str):
        if TOMLParser.has_var(v):
          s = v
          for kk, vv in self.vars.items():
            s = s.replace(kk, vv)
          new_dict[k] = s
          if TOMLParser.has_var(s):
            self.cnt += 1
          else:
            self.vars[TOMLParser.LEFT_MARKER + k + TOMLParser.RIGHT_MARKER] = s
        else:
          if TOMLParser.DROPBOX_MARKER in v:
            v = v.replace(TOMLParser.DROPBOX_MARKER, str(TOMLParser._find_dropbox_root()))
          new_dict[k] = v
          self.vars[TOMLParser.LEFT_MARKER + k + TOMLParser.RIGHT_MARKER] = v
      else:
        new_dict[k] = self._traverse(v)
    return new_dict


if __name__ == '__main__':
  tmlfle = TOMLParser(Path('../tests/data/merkur_global_config.toml'))
  # print(json.dumps(tmlfle.parse(),indent=2))
  # tmlfle.dump(Path('/home/arthur/aa.toml'))
  print(tmlfle.dumps())


