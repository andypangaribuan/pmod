# Copyright (c) 2025.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.

# %%
import os
import sys
sys.path.insert(1, os.path.split(
    os.path.dirname(os.path.abspath(__file__)))[0])

# %%
# test eval print
from pmod import eval
from pmod.eval import HttpStyle as style

url = 'https://ifconfig.me'
header = {
  'Content-Type': 'application/json'
}

_, _ = eval.get(url=url, style=style.with_header, header=header)

# %%