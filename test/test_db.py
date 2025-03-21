# Copyright (c) 2025.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.

# %%
import pmod
import os
import sys
sys.path.insert(1, os.path.split(
    os.path.dirname(os.path.abspath(__file__)))[0])
# sys.path.insert(1, '..')


env = pmod.get_env('.env')
dbx = pmod.DBX(name=env['DB_NAME'], host=env['DB_HOST'], port=env['DB_PORT'],
               usr=env['DB_USER'], pwd=env['DB_PASS'], tz=env['DB_TZ'])

query: str = 'SELECT * FROM nc_3tf8__member ORDER BY house'
rows, err = dbx.fetches(query=query)

if err is not None:
  print(err)
else:
  pmod.print_table(rows)


# %%
