#!/usr/bin/env python3

# ---------------------------------------------
# Copyright Arthur Rabatin. See www.rabatin.com
# ---------------------------------------------

class CLCommandList:

  PARAMTYPE_ANY = 'ANY'
  PARAMTYPE_NONE = 'NONE'
  PARAMTYPE_ONEORMORE = 'ONEORMORE'
  PARAMTYPE_EXACT = 'EXACT'

  def __init__(self, sys_argv:list = None):
    self.title = None
    self.allow_default = False
    self.command_program = ''
    self.command_param = ''
    self.commands = {}
    self.cached_command_params = []
    if sys_argv:
      self.process_sys_argv(sys_argv)
    self.command_spec = []

  def set_title(self, title:str):
    self.title = title
    return self

  def allow_default(self, allow_default:bool):
    self.allow_default = allow_default
    return self

  def add_command(self, command_string:str,
                  description:str,
                  mandatory:bool,
                  position:int,
                  paramtype:str,
                  param_exact_count:int):
    if paramtype != CLCommandList.PARAMTYPE_EXACT and param_exact_count is not None:
      raise RuntimeError('paramtype != CLCommandList.PARAMTYPE_EXACT and param_exact_count is not None')
    for cmd in self.command_spec:
      if cmd['command_string'] == command_string:
        raise RuntimeError(f'Duplicate command string {command_string}')
    self.command_spec.append({
      'command_string':command_string,
      'description':description,
      'mandatory':mandatory,
      'position':position,
      'paramtype':paramtype,
      'param_exact_count':param_exact_count
    })
    return self

  def process_sys_argv(self, sys_argv:list):
    self.command_program = sys_argv[0]
    self.command_param = sys_argv[1:]
    self.commands = {}
    self.cached_command_params = []

    commands = []
    current_new_command = {
      'command': '__default__',
      'params': list()
    }
    for elem in self.command_param:
      if elem.startswith('--'):
        commands.append(current_new_command)
        current_new_command = {
          'command': elem[2:],
          'params':list()
        }
      else:
        current_new_command['params'].append(elem)
    commands.append(current_new_command)
    for comm in commands:
      if comm['command'] == '__default__':
        if len(comm['params']) > 0:
          self.commands['__default__'] = comm['params']
      else:
        self.commands[comm['command']] = comm['params']


  def has(self, command:str):
    self.cached_command_params = self.commands.get(command, [])
    return command in self.commands

  def has_default(self):
    return self.has('__default__')

  def param(self, indx:int):
    return self.cached_command_params[indx]

  def commandline(self):
    cl = self.command_program + ' ' + ' '.join(self.command_param)
    return cl

  def print_commands(self):
    for c in self.commands:
      print(c)
