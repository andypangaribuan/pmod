# Copyright (c) 2025.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.

import json
import rich
import requests
import sys
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.lexers.data import JsonLexer
from pygments.formatters import TerminalFormatter
from dotenv import dotenv_values
from typing import cast, TypeVar, Callable, Coroutine, Generic
from unsync import unsync
from grpclib.client import Channel


T = TypeVar("T")
Y = TypeVar("Y")


def get_env(*args) -> dict:
  env = {}
  for arg in args:
    env.update(dotenv_values(arg))
  return env


def get(url: str, style: int = 0, header: dict[str, str] = None, params: any = None):
  r = requests.get(url, headers=header, params=params)
  __show(r, style)
  return r.status_code, r.text


def post(url: str, style: int = 0, header: dict[str, str] | None = None, json: any = None, files: any = None, params: any = None):
  r = requests.post(url, headers=header, json=json, files=files, params=params)
  __show(r, style)
  return r.status_code, r.text


def print_json(val: str):
  try:
    json_object = json.loads(val)
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    print(highlight(json_str, JsonLexer(), TerminalFormatter()))
  except Exception as _:
    try:
      rich.print_json(val)
    except Exception as _:
      rich.print(val)


def print_make(val: str):
  print(highlight(val, get_lexer_by_name("make"), TerminalFormatter()))


def replace_env_value(file_path: str, key: str, value: str, print_rewrite: bool = False):
  index = -1
  lines = []

  with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for i, line in enumerate(lines):
      if key in line:
        index = i
        break

  if index != -1:
    lines[index] = f'{key}={value}\n'
    with open(file_path, 'w', encoding='utf-8') as file:
      file.writelines(lines)
      if print_rewrite:
        print('rewrite')


def __show(r: requests.Response, style: int):
  match style:
    case 0:
      print(f'status: {r.status_code}')
      print_json(json.dumps(dict(r.headers)))

      print('\n\n')
      print_json(r.text)

    case 1:
      print(f'status: {r.status_code}')
      print_json(r.text)

    case 2:
      print_json(r.text)


class GrpcClient(Generic[Y]):
  def __init__(self, url: str, stub: Y):
    self.host = url.split(':')[0]
    self.port = int(url.split(':')[1])
    self.stub = stub

  def call(self, type: T, func: Callable[[Y], Coroutine]) -> T:
    try:
      res = self.__exec(func).result()
      return cast(type, res)
    except Exception as e:
      message = str(e)
      sys.exit('unable to connect to grpc server' if 'Connect call failed' in message else message)

  @unsync
  async def __exec(self, call: Callable[[Y], Coroutine]):
    channel = Channel(host=self.host, port=self.port, ssl=self.port == 443)
    service = self.stub(channel=channel)
    res = await call(service)
    channel.close()
    return res
