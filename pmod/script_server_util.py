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
import subprocess
from typing import Any, Optional
from packaging.version import Version
from pmod.script_server_model import *


class ScriptServerUtil:
    def sh_get(self, cmd: str) -> tuple[str, str]:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return process.communicate()


    def join_words(self, items: list[str], unionSeparator: str = ',', lastSeparator: str = 'and') -> str:
        if len(items) > 2:
            return '%s %s %s' % (f'{unionSeparator} '.join(items[:-1]), lastSeparator, items[-1])
        else:
            return f' {lastSeparator} '.join(items)


    def version_parse(self, ver: str) -> tuple[Version, bool]:
        try:
            v = Version(ver)
            return v, True
        except Exception:
            return None, False


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
    

    def get_version_text(self, ver: Version) -> str:
        if ver is None:
            return ''
        if ver.pre is not None:
            return f'{ver.major}.{ver.minor}.{ver.micro}.{ver.pre[0]}{ver.pre[1]}'
        return ver.public


    def gitlab_diff_branch(self, conf: ScriptServerConf, branch_from: str, branch_to: str) -> tuple[Optional[int], Optional[str]]:
        url: str = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/compare?from={branch_from}&to={branch_to}&straight=true'
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


    def gitlab_find_tag(self, conf: ScriptServerConf, ver: Version) -> tuple[bool, str]:
        version: str = f'v{self.get_version_text(ver)}'
        url: str = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/tags/{version}'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.get(url, headers=headers)
        jres = res.json()

        match res.status_code:
            case 404:
                message = self.dict_value(jres, ['message'])
                if message == '404 Tag Not Found':
                    return False, None
                
            case 200:
                name = self.dict_value(jres, ['name'])
                if name == version:
                    return True, None

        return False, f'http code: {res.status_code}\nresponse: {jres}'

    def gitlab_delete_tag(self, conf: ScriptServerConf, ver: Version) -> Optional[str]:
        version: str = f'v{self.get_version_text(ver)}'
        url = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/tags/{version}'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.delete(url, headers=headers)

        if res.status_code not in [200, 202, 204]:
            resJson: Any = None
            try:
                resJson = res.json()
                return f'http code: {res.status_code}, response: {resJson}'
            except Exception:
                return f'http code: {res.status_code}, response: {res.text}'

        return None


    def gitlab_create_tag(self, conf: ScriptServerConf, ver: Version, branch: str) -> Optional[str]:
        version: str = f'v{self.get_version_text(ver)}'
        url = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/tags?tag_name={version}&ref={branch}'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.post(url, headers=headers)
        if res.status_code not in [200, 201]:
            return f'http code: {res.status_code}, response: {res.json()}'

        try:
            version_name = self.dict_value(res.json(), ['name'])
            if version_name == version:
                return None
            return f'http code: {res.status_code}, response: {res.json()}'
        except Exception:
            return f'invalid output: {res.json()}'



    def get_last_index_version(self, ver: Version) -> tuple[int, int]:
        last_index = len(ver.release) - 1
        return last_index, ver.release[last_index]


    def increase_version(self, ver: Version) -> str:
        if ver.pre is None:
            last_index, value = self.get_last_index_version(ver)
            ls = [str(v) for v in ver.release]
            ls[last_index] = str(value + 1)
            return '.'.join(ls)

        pre_name, pre_ver = ver.pre
        ls = [str(v) for v in ver.release]
        new_version = '.'.join(ls)
        return f'{new_version}.{pre_name}{pre_ver+1}'


    def fetch_latest_image_version(self, env: ScriptServerEnv, env_name: str) -> tuple[Version, str]:
        match env.image_registry:
            case 'gcp-artifact-registry':
                print(f'\n→ call gcloud api: get image last version on {env_name}')

                cmd: str = 'chroot /hostfs /bin/bash -c "docker exec -it %s %s"'
                cmd = cmd % (
                    env.container_cloud_sdk,
                    'gcloud artifacts tags list --location=%s --repository=%s --package=%s --format=\'table(TAG)\'',
                )
                cmd = cmd % (env.gcp_artifact_registry_location, env.gcp_artifact_registry_repository, env.gcp_artifact_registry_package)

                out, err = self.sh_get(cmd)
                if err != "":
                    return None, err
                if 'TAG' not in out:
                    return None, f'TAG not found in {out}'
                
                lines = out.splitlines()
                image_version: Version = None

                for line in lines:
                    try:
                        version = Version(line)
                        if image_version is None:
                            image_version = version
                            continue

                        if version > image_version:
                            image_version = version
                    except Exception as err:
                        ...

                return image_version, None

            case _:
                return None, 'unhandled logic'
