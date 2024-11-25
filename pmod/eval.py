#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

import json
import rich
import requests
from dotenv import dotenv_values



def get_env(*args) -> dict:
    env = {}
    for arg in args:
        env.update(dotenv_values(arg))
    return env


def get(url: str, style: int = 0, header: dict[str, str] = None):
    r = requests.get(url, headers=header)
    __show(r, style)
    return r.status_code, r.text


def post(url: str, style: int = 0, header: dict[str, str] | None = None, json: any = None, files: any = None, params: any = None):
    r = requests.post(url, headers=header, json=json, files=files, params=params)
    __show(r, style)
    return r.status_code, r.text


def print_json(val: str):
    try:
        rich.print_json(val)
    except Exception as _:
        rich.print(val)


def __show(r: requests.Response, style: int):
    match style:
        case 0:
            print(f'status: {r.status_code}')
            print_json(json.dumps(dict(r.headers)))

            print('\n\n')
            print_json(r.text)

        case 1:
            print_json(r.text)
