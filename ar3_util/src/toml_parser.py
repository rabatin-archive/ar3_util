# ########################################################################
# (C) Arthur Rabatin - All Rights Reserved. www.rabatin.com
# See LICENSE.txt for License Information
# #########################################################################

"""
Simple TOML dictionary parser that provides for variable interpolation and interpolation of a DROPBOX keyword
"""

from pathlib import Path
import os
import toml
import json
from ar3_util.src.os_detector import is_linux, is_windows, os_name

class TOMLParser:
  """
  Simple TOML dictionary parser that provides for variable interpolation and interpolation of a DROPBOX keyword
  to insert host/user account specific Dropbox directories
  For example
  my_special_directory = '/mnt/special'
  my_other_directory = '<?my_special_directory?>/other/dir'
  This parser will interpolate my_other_directory to be  '/mnt/special/other/dir'
  Any combination of such variables is allowed (it will parse recursively until all variables are interpolated).

  The special variable <#DROPBOX#> will be interpreted to mean a private Dropbox account and will be replaced with
  the local Dropbox location. If no Dropbox is installed, it will throw an exception
  """

  DROPBOX_MARKER = '<#DROPBOX#>'
  LEFT_MARKER = '<?'
  RIGHT_MARKER = '?>'

  def __init__(self, toml_file:Path):
    self.vars = {}
    self.cnt = 0
    with open(toml_file, 'r', encoding='utf-8') as f:
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
    with open(dropbox_spectfile, 'r', encoding='utf-8') as f:
      dropbox_config = json.load(f)
    return Path(dropbox_config['personal']['path'])

  @staticmethod
  def has_var(s: str) -> bool:
    return TOMLParser.LEFT_MARKER in s and TOMLParser.RIGHT_MARKER in s

  def parse(self):
    if self.parsed_dict_cache is None:
      self.parsed_dict_cache = self._iterative_parse(self.tomldata)
    return self.parsed_dict_cache

  def dump(self, filename:Path, exist_ok:bool=False):
    if not exist_ok:
      if filename.is_file():
        raise RuntimeError(f'Output file already exists {filename}')
    with open(filename, 'w', encoding='utf-8') as f:
      toml.dump(self.parse(), f)

  def dumps(self):
    return toml.dumps(self.parse())

  def _iterative_parse(self, d_:dict):
    self.cnt = 99
    new_dict = {}
    while self.cnt != 0:
      self.cnt = 0
      new_dict = self._traverse(d_)
    return new_dict

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
  tmlfle = TOMLParser(Path('../../tests/data/merkur_global_config.toml'))
  # print(json.dumps(tmlfle.parse(),indent=2))
  # tmlfle.dump(Path('/home/arthur/aa.toml'))
  print(tmlfle.dumps())


