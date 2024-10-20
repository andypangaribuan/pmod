#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

from pmod.script_server_model import *
from pmod.script_server_util import *


class ScripServer:
    __util                    : ScriptServerUtil = ScriptServerUtil()
    __conf                    : ScriptServerConf = None
    __stg_env                 : ScriptServerEnv  = None
    __rc_env                  : ScriptServerEnv  = None
    __prod_env                : ScriptServerEnv  = None
    __repository_type         : str              = None
    __selected_env            : ScriptServerEnv  = None
    __selected_env_code       : str              = None
    __workflow_env_code       : str              = None
    __current_image_version   : str              = None
    __below_env_image_version : str              = None
    __above_env_image_version : str              = None


    def __init__(self, conf: ScriptServerConf, stg_env: ScriptServerEnv = None, rc_env: ScriptServerEnv = None, prod_env: ScriptServerEnv = None):
        self.__conf     = conf
        self.__stg_env  = stg_env
        self.__rc_env   = rc_env
        self.__prod_env = prod_env


    def run(self):
        self.__validate()
        self.__select_env()
        self.__gitlab_diff_branch()
        self.__get_image_version()
        self.__diff_branch_with_tag_version()
        self.__get_user_next_version()


    def __validate(self):
        match self.__conf.git_repo[:10]:
            case 'gitlab.com':
                self.__repository_type = 'gitlab'
            case _:
                print(f'\n🔴 only support gitlab.com repository')
                exit()

        if self.__stg_env is None and self.__rc_env is None and self.__prod_env is None:
            print(f'\n🔴 have no env configured')
            exit()

        if self.__stg_env is not None and self.__rc_env is not None and self.__prod_env is not None:
            self.__workflow_env_code = 'srp'
        elif self.__stg_env is not None and self.__prod_env is not None:
            self.__workflow_env_code = 'sp'
        elif self.__stg_env is not None:
            self.__workflow_env_code = 's'
        else:
            print(f'\n🔴 no matching workflow env')
            exit()

        if self.__selected_env.hosting_type != 'gcp':
            print(f'\n🔴 hosting type support: gcp')
            exit()

        if self.__selected_env.deployment_type != 'k8s':
            print(f'\n🔴 hosting type support: gcp')
            exit()

        if self.__selected_env.container_cloud_sdk is None:
            print(f'\n🔴 empty container_cloud_sdk')
            exit()
        
        if self.__stg_env is not None and self.__stg_env.image_registry != 'gcp-artifact-registry':
            print(f'\n🔴 [stg-env] supported image registry: gcp-artifact-registry')
            exit()
        
        if self.__rc_env is not None and self.__rc_env.image_registry != 'gcp-artifact-registry':
            print(f'\n🔴 [rc-env] supported image registry: gcp-artifact-registry')
            exit()
        
        if self.__prod_env is not None and self.__prod_env.image_registry != 'gcp-artifact-registry':
            print(f'\n🔴 [prod-env] supported image registry: gcp-artifact-registry')
            exit()


    def __select_env(self):
        match self.__workflow_env_code:
            case 'srp':
                self.__selected_env_code = self.__util.choose('[ask] choose environment?', ['stg', 'rc', 'prod'])
            case 'sp':
                self.__selected_env_code = self.__util.choose('[ask] choose environment?', ['stg', 'prod'])
            case 's':
                self.__selected_env_code = self.__util.choose('[ask] choose environment?', ['stg'])
        
        if self.__selected_env_code is None:
            print(f'\n🔴 no environment selected, terminated!')
            exit()
        
        match self.__selected_env_code:
            case 'stg':
                self.__selected_env = self.__stg_env
            case 'rc':
                self.__selected_env = self.__rc_env
            case 'prod':
                self.__selected_env = self.__prod_env


    def __gitlab_diff_branch(self):
        print(f'\ncall gitlab api: diff branch ({self.__selected_env.git_prev_branch} → {self.__selected_env.git_branch})')
        diffs, err = self.__util.gitlab_diff_branch(self.__conf, self.__selected_env.git_prev_branch, self.__selected_env.git_branch)
        if err is not None:
            print(f'🔴 error: {err}')
            exit()
        
        if diffs == 0:
            print(f'no changes')
        else:
            self.__util.gitlab_create_mr(self.__conf, self.__selected_env)


    def __get_image_version(self):
        current : list = None
        below   : list = None
        above   : list = None

        match self.__workflow_env_code:
            case 'srp':
                match self.__selected_env_code:
                    case 'stg':
                        current = [self.__stg_env, 'stg']
                        above = [self.__rc_env, 'rc']
                    
                    case 'rc':
                        current = [self.__rc_env, 'rc']
                        below = [self.__stg_env, 'stg']
                    
                    case 'prod':
                        current = [self.__prod_env, 'prod']
                        below = [self.__rc_env, 'rc']

            case 'sp':
                match self.__selected_env_code:
                    case 'stg':
                        current = [self.__stg_env, 'stg']
                        above = [self.__prod_env, 'prod']
                        
                    case 'prod':
                        current = [self.__prod_env, 'prod']
                        below = [self.__stg_env, 'stg']

            case 's':
                match self.__selected_env_code:
                    case 'stg':
                        current = [self.__stg_env, 'stg']

        err                    : str = None
        current_version        : str = None
        below_env_image_version: str = None
        above_env_image_version: str = None

        current_version, err = self.__util.fetch_latest_image_version(current[0], current[1])
        if err is not None:
            print(f'🔴 error: {err}')
            exit()

        if below is not None:
            below_env_image_version, err = self.__util.fetch_latest_image_version(below[0], below[1])
            if err is not None:
                print(f'🔴 error: {err}')
                exit()
        
        if above is not None:
            above_env_image_version, err = self.__util.fetch_latest_image_version(above[0], above[1])
            if err is not None:
                print(f'🔴 error: {err}')
                exit()

        self.__current_image_version   = current_version
        self.__below_env_image_version = below_env_image_version
        self.__above_env_image_version = above_env_image_version


    def __diff_branch_with_tag_version(self):
        print(f'\n→ call gitlab api: diff (branch:{self.__selected_env.git_branch} → tag:v{self.__current_image_version})')
        diffs, err = self.__util.gitlab_diff_branch(self.__conf, self.__selected_env.git_branch, f'v{self.__current_image_version}')
        if err is not None:
            print(f'🔴 error: {err}')
            exit()

        if diffs == 0:
            print(f"no changes from branch '{self.__selected_env.git_branch}' with last_version 'v{self.__current_image_version}'")
            exit()

        print(f'have {diffs} diff, good to go')


    def __get_user_next_version(self):
        match self.__workflow_env_code:
            case 'srp'


