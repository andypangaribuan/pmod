'''
Copyright (c) 2025.
Created by Andy Pangaribuan (iam.pangaribuan@gmail.com)
https://github.com/apangaribuan

This product is protected by copyright and distributed under
licenses restricting copying, distribution and decompilation.
All Rights Reserved.
'''

import json
import rich
import requests
import jsonpickle
import sys
from enum import Enum
from pygments import highlight
from pygments.lexers import get_lexer_by_name
# from pygments.lexers.data import JsonLexer
from pygments.formatters import TerminalFormatter
from dotenv import dotenv_values
from typing import cast, TypeVar, Callable, Coroutine, Generic
from unsync import unsync
from grpclib.client import Channel


T = TypeVar("T")
Y = TypeVar("Y")


class HttpStyle(Enum):
    hidden = -1
    with_header = 1
    content_only = 2


def get_env(*args) -> dict:
    env = {}
    for arg in args:
        env.update(dotenv_values(arg))
    return env


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


def get(url: str, style: HttpStyle = HttpStyle.hidden, header: dict[str, str] | None = None, params: any = None):
    req = requests.get(url, headers=header, params=params)
    __show('get', req, style)
    return req.status_code, req.text


def post(url: str, style: HttpStyle = HttpStyle.hidden, header: dict[str, str] | None = None, body: any = None, files: any = None, params: any = None):
    req = requests.post(url, headers=header, json=body, files=files, params=params)
    __show('post', req, style)
    return req.status_code, req.text


def put(url: str, style: HttpStyle = HttpStyle.hidden, header: dict[str, str] | None = None, body: any = None, files: any = None, params: any = None):
    req = requests.put(url, headers=header, json=body, files=files, params=params)
    __show('put', req, style)
    return req.status_code, req.text


def path(url: str, style: HttpStyle = HttpStyle.hidden, header: dict[str, str] | None = None, body: any = None, files: any = None, params: any = None):
    req = requests.patch(url, headers=header, json=body, files=files, params=params)
    __show('patch', req, style)
    return req.status_code, req.text


def delete(url: str, style: HttpStyle = HttpStyle.hidden, header: dict[str, str] | None = None, params: any = None):
    req = requests.delete(url, headers=header, params=params)
    __show('delete', req, style)
    return req.status_code, req.text


def print_json(val: str):
    try:
        json_object = json.loads(val)
        json_str = json.dumps(json_object, indent=2, sort_keys=True)
        print(highlight(json_str, get_lexer_by_name("json"), TerminalFormatter()))
    except Exception as _:
        try:
            rich.print_json(val)
        except Exception as _:
            rich.print(val)


def print_object(obj, removeKeysStartingWith: str | None = None):
    try:
        json_string = jsonpickle.encode(obj, unpicklable=False)
        json_object = json.loads(json_string)
        if removeKeysStartingWith is not None:
            json_object = __remove_keys_starting_with(json_object, removeKeysStartingWith)

        json_str = json.dumps(json_object, indent=2, sort_keys=True)
        print(highlight(json_str, get_lexer_by_name("make"), TerminalFormatter()))
    except Exception as _:
        try:
            rich.print_json(obj)
        except Exception as _:
            rich.print(obj)


def print_make(val: str):
    print(highlight(val, get_lexer_by_name("make"), TerminalFormatter()))


def __show(http_method: str, response: requests.Response, style: HttpStyle):
    match style:
        case HttpStyle.with_header:
            print(f'{response.status_code}: {http_method} {response.url}\n')
            print_json(json.dumps(dict(response.headers)))
            print_json(response.text)

        case HttpStyle.content_only:
            print(f'{response.status_code}: {http_method} {response.url}\n')
            print_json(response.text)


def __remove_keys_starting_with(data, prefix):
    if isinstance(data, dict):
        keys_to_remove = [key for key in data if key.startswith(prefix)]
        for key in keys_to_remove:
            del data[key]
        for value in data.values():
            __remove_keys_starting_with(value, prefix)
    elif isinstance(data, list):
        for item in data:
            __remove_keys_starting_with(item, prefix)
    return data


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
