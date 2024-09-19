#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

from dotenv import dotenv_values


def get_env(*args) -> dict:
    env = {}
    for arg in args:
        env.update(dotenv_values(arg))
    return env

