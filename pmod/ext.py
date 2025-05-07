'''
Copyright (c) 2025.
Created by Andy Pangaribuan (iam.pangaribuan@gmail.com)
https://github.com/apangaribuan

This product is protected by copyright and distributed under
licenses restricting copying, distribution and decompilation.
All Rights Reserved.
'''

from dotenv import dotenv_values


def get_env(*args) -> dict:
    env = {}
    for arg in args:
        env.update(dotenv_values(arg))
    return env


def print_table(data: dict, columns: list = None):
    if not columns:
        columns = list(data[0].keys() if data else [])
    items = [columns]

    for item in data:
        items.append(['' if item[col] is None else str(
            item[col]).replace('\n', ' | ') for col in columns])

    sizes = [max(map(len, col)) for col in zip(*items)]
    formatter = ' | '.join(["{{:<{}}}".format(i) for i in sizes])
    items.insert(1, ['-' * i for i in sizes])

    for item in items:
        print(formatter.format(*item))
