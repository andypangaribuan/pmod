# import pmod
import os
import sys
sys.path.insert(1, os.path.split(
    os.path.dirname(os.path.abspath(__file__)))[0])
# sys.path.insert(1, '..')
import pmod


env = pmod.get_env('.env')

# %%
a1 = pmod.add(3, 4)
print(f'1 + 2 = {a1}')
