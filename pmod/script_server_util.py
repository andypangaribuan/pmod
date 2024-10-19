#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

import time


class ScriptServerUtil:
    def join_words(self, items: list[str], unionSeparator: str = ',', lastSeparator: str = 'and') -> str:
        if len(items) > 2:
            return '%s %s %s' % (f'{unionSeparator} '.join(items[:-1]), lastSeparator, items[-1])
        else:
            return f' {lastSeparator} '.join(items)

    def choose(self, message: str, items: list[str]) -> str:
        print(f'{message} ({self.join_words(items, lastSeparator="or")})')
        selected: str = None
        while selected is None:
            answer = input()
            if answer in items:
                selected = answer
            else:
                print('🔴 invalid input, please try again')
                time.sleep(3)
                self.remove_current_line(2)
        return selected

    def remove_current_line(self, size: int = 1):
        if size < 1:
            return
        for _ in range(size):
            print('\033[1A' + '\033[K', end='')
