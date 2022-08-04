import platform


def is_linux():
  return _is_specific_os('Linux')

def is_windows():
  return _is_specific_os('Windows')

def os_name():
  return platform.system()

def _is_specific_os(osname: str):
  if platform.system() not in ['Windows', 'Linux']:
    raise RuntimeError(f'Unexpected System found: {platform.system()}')
  return platform.system() == osname


