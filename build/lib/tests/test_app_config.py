#!/usr/bin/env python3

import os
from pathlib import Path
# ---------------------------------------------
# Copyright Arthur Rabatin. See www.rabatin.com
# ---------------------------------------------
from unittest import TestCase

import yaml

import ar3_util.app_config


class TestAppConfig(TestCase):

  def test_replace_string_token_vars(self):
    test_cases = [
      {
        'test_str': '$<a>_B_C_$<d>_1_2_$<twenty>_aaa_$<w>?',
        'expected': 'A_B_C_D_1_2_20_aaa_WHAT???',
        'replace_dict': {
          'a': 'A',
          'd': 'D',
          'twenty': '20',
          'w': 'WHAT??'
        }
      },
      {
        'test_str': 'abcd',
        'expected': 'abcd',
        'replace_dict': {
        }
      },
      {
        'test_str': '',
        'expected': '',
        'replace_dict': {
        }
      }
    ]
    for test in test_cases:
      t = ar3_util.app_config.AppConfig._replace_string_token_vars(test['test_str'],
                                                                   test['replace_dict'], token_start=ar3_util.app_config.AppConfig.STD_TOKEN_START,
                                                                   token_end=ar3_util.app_config.AppConfig.STD_TOKEN_END)
      if t != test['expected']:
        raise RuntimeError(f"{t} is not as expected {test['expected']}")

  def test_load_from_file_and_parse(self):
    os.environ['test_var_123'] = 'interpolated_test_var_123'
    os.environ['test_var_12345'] = 'interpolated_test_var_12345'
    os.environ['test_var_123456'] = 'interpolated_test_var_123456'
    fn = Path('data/test_config_1.yaml')
    compare_fn = Path('data/compare_test_config_1.yaml')

    appconfig = ar3_util.app_config.AppConfig.create_appconfig_from_configfile(fn)

    # Only use this when re-creating new test data
    # with open(compare_fn, 'w') as f:
    #   yaml.dump(appconfig.data, f)

    with open(compare_fn, 'r') as f:
      compare_data = yaml.load(f, Loader=yaml.FullLoader)

    self.assertDictEqual(appconfig.data, compare_data)
#
