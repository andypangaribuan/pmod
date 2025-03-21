# Copyright (c) 2025.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.

# %%
# test eval print
import pmod


from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter

result = f'''
process     : BUY
amount_type : currency
amount_value: 1000
total_unit  : 100.123
'''

print(highlight(result, get_lexer_by_name("make"), TerminalFormatter()))



# %%