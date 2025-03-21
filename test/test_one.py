# Copyright (c) 2025.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.

import pmod
import os
import sys
sys.path.insert(1, os.path.split(
    os.path.dirname(os.path.abspath(__file__)))[0])
# sys.path.insert(1, '..')


env = pmod.get_env('.env')

# %%
a1 = pmod.add(3, 4)
print(f'1 + 2 = {a1}')
