#!/usr/bin/env python3

# ---------------------------------------------
# Copyright Arthur Rabatin. See www.rabatin.com
# ---------------------------------------------

"""
AppConfig class definition
"""

import os
import sys
from pathlib import Path

import yaml


class AppConfig:
  """
  General purposes yaml loader to allows to speciy environment variables or other
  variables to be used.

  For example
    root_dir: $(HOME_DIR)
    cache_folder: $<root_dir>/my_cache
    special_folder: $(cache_folder)/special_folder
  will resolve to:
    root_dir: /home/users/arthur
    cache_folder: /home/users/arthur/my_cache
    special_folder: /home/users/arthur/my_cache/special_folder
  This assumes an environment variable 'HOME_DIR' defined as /home/users/arthur
  """

  ENV_TOKEN_START = '$('
  ENV_TOKEN_END = ')'
  STD_TOKEN_START = '$<'
  STD_TOKEN_END = '>'

  @staticmethod
  def _parse_str_for_variable(source_str, token_start_id, token_end_id):
    if token_start_id not in source_str:
      return []
    tokens = []
    look_pos = 0
    while True:
      token_start_pos = source_str.find(token_start_id, look_pos)
      if token_start_pos < 0:
        break
      token_end_pos = source_str.find(token_end_id, token_start_pos)
      if token_end_pos < 0:
        raise RuntimeError(f'Missing matching token end {token_end_id} in {source_str}')
      tokens.append({
        'token_str': source_str[token_start_pos + len(token_start_id):token_end_pos],
        'token_start_pos': token_start_pos,
        'token_end_pos': token_end_pos
      })
      look_pos = token_start_pos + len(token_start_id)
    for ix, token in enumerate(tokens[:-1]):
      follow_string = source_str[
                      token['token_end_pos'] + 1:tokens[ix + 1]['token_start_pos']]
      token['follow_string'] = follow_string
    tokens[len(tokens) - 1]['follow_string'] = source_str[tokens[len(tokens) - 1][
                                                            'token_end_pos'] + 1: len(
      source_str)]
    return tokens

  @staticmethod
  def _replace_string_token_vars(source_str, token_dict, token_start, token_end):
    new_string = []
    for token in AppConfig._parse_str_for_variable(source_str, token_start, token_end):
      if token['token_str'] not in token_dict:
        raise RuntimeError(
          f"Interpolating {source_str}: "
          f"could not find replacement for "
          f"token \'{token['token_str']}\' in {str(list(token_dict.keys()))}")
      new_string.append(token_dict[token['token_str']])
      new_string.append(token['follow_string'])
    if new_string:
      return ''.join(new_string)
    else:
      return source_str

  @staticmethod
  def _iterate_dict_pairs(d: dict, token_dict: dict, token_start_id,
                          token_end_id):
    new_data = {}
    new_token_dict = token_dict
    new_token_dict.update(token_dict)
    for k, v in d.items():
      if isinstance(v, str):
        new_data[k] = AppConfig._replace_string_token_vars(v, token_dict, token_start_id,
                                                           token_end_id)
        new_token_dict[k] = new_data[k]
      elif isinstance(v, dict):
        ret_data, ret_token_dict = AppConfig._iterate_dict_pairs(v, new_token_dict,
                                                                 token_start_id,
                                                                 token_end_id)
        new_data[k] = ret_data
        new_token_dict.update(ret_token_dict)
      else:
        raise RuntimeError(f'Unknown object type {type(v)}')
    return (new_data, new_token_dict)

  @staticmethod
  def _verify_python_version():
    invalid_version = False
    if sys.version_info.major >= 3:
      if sys.version_info.minor < 7:
        invalid_version = True
    else:
      invalid_version = True
    if invalid_version:
      raise RuntimeError(
        f'Need at least Python version 3.7 and '
        f'not {sys.version_info.major}.{sys.version_info.minor}. '
        f'Needs ordered dictionary by default when leading dicts from YAML')

  @staticmethod
  def _parse_yaml_configfile(config_file: Path):
    AppConfig._verify_python_version()
    with open(config_file) as f:
      data = yaml.load(f, Loader=yaml.FullLoader)
    new_data, unused_replace_token_dict = \
      AppConfig._iterate_dict_pairs(d=data,
                                    token_dict=os.environ,
                                    token_start_id=AppConfig.ENV_TOKEN_START,
                                    token_end_id=AppConfig.ENV_TOKEN_END)
    new_data2, unused_replace_token_dict = \
      AppConfig._iterate_dict_pairs(d=new_data,
                                    token_dict={},
                                    token_start_id=AppConfig.STD_TOKEN_START,
                                    token_end_id=AppConfig.STD_TOKEN_END)
    return new_data2

  @staticmethod
  def create_appconfig_from_configfile(yaml_configfile: Path):
    return AppConfig(AppConfig._parse_yaml_configfile(yaml_configfile))

  def __init__(self, config_data_dict: dict):
    self.data = config_data_dict
