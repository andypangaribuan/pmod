#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

import time
import requests
from typing import Optional
from pmod.script_server_model import *


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


    def dict_value(self, dictionary, keys: list[str]):
        value = None
        nested_dict = dictionary

        for key in keys:
            try:
                nested_dict = nested_dict[key]
                value = nested_dict
            except KeyError:
                return None

        return value


    def gitlab_diff_branch(self, conf: ScriptServerConf, selected_env: ScriptServerEnv) -> tuple[Optional[int], Optional[str]]:
        url: str = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/compare?from={selected_env.git_prev_branch}&to={selected_env.git_branch}&straight=true'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return None, f'http code: {res.status_code}'

        diffs = self.dict_value(res.json(), ['diffs'])
        return len(diffs), None


    def gitlab_create_mr(self, conf: ScriptServerConf, selected_env: ScriptServerEnv):
        mr_url = f'https://{conf.git_repo}/-/merge_requests/new?merge_request'
        source = f'source_project_id%5D={conf.git_id}&merge_request%5Bsource_branch%5D={selected_env.git_prev_branch}'
        target = f'target_project_id%5D={conf.git_id}&merge_request%5Btarget_branch%5D={selected_env.git_branch}'
        url    = f'{mr_url}%5B{source}&merge_request%5B{target}'

        print(f"have new files from branch '{selected_env.git_prev_branch}' to branch '{selected_env.git_branch}'")
        print(f'🟠 please do manual MR')
        print(f'url: {url}')
        exit()
