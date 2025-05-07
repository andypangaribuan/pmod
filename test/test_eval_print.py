'''
Copyright (c) 2025.
Created by Andy Pangaribuan (iam.pangaribuan@gmail.com)
https://github.com/apangaribuan

This product is protected by copyright and distributed under
licenses restricting copying, distribution and decompilation.
All Rights Reserved.
'''

# %%
import os
import sys
sys.path.insert(1, os.path.split(
    os.path.dirname(os.path.abspath(__file__)))[0])

# %%
# test eval print
from pmod import eval

eval.print_make(f'''
process     : BUY
amount_type : currency
amount_value: 1000
total_unit  : 100.123
''')



# %%