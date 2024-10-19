#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

from pmod.script_server_util import *


class ScriptServerConf:
    project_name    : str = None
    timezone        : str = None
    git_repo        : str = None
    git_id          : str = None
    git_user        : str = None
    git_pass        : str = None
    dockerfile_path : str  = None


class ScriptServerEnv:
    timezone            : str = None
    hosting_type        : str = None # types: gcp
    deployment_type     : str = None # types: k8s
    container_cloud_sdk : str = None  # only for hosting_type = gcp
    git_prev_branch     : str = None
    git_branch          : str = None


class ScripServer:
    __util            : ScriptServerUtil = ScriptServerUtil()
    __conf            : ScriptServerConf = None
    __stg_env         : ScriptServerEnv  = None
    __rc_env          : ScriptServerEnv  = None
    __prod_env        : ScriptServerEnv  = None
    __repository_type : str              = None
    __selected_env    : ScriptServerEnv  = None

    def __init__(self, conf: ScriptServerConf, stg_env: ScriptServerEnv = None, rc_env: ScriptServerEnv = None, prod_env: ScriptServerEnv = None):
        self.__conf     = conf
        self.__stg_env  = stg_env
        self.__rc_env   = rc_env
        self.__prod_env = prod_env

    def run(self):
        match self.__conf.git_repo[:10]:
            case 'gitlab.com':
                self.__repository_type = 'gitlab'
            case _:
                print('only support gitlab.com repository')
                exit()

        if self.__stg_env is None and self.__rc_env is None and self.__prod_env is None:
            print('have no env configured')
            exit()
        
        if self.__stg_env is not None and self.__rc_env is not None and self.__prod_env is not None:
            self.__select_env(type='srp')
        elif self.__stg_env is not None and self.__prod_env is not None:
            self.__select_env(type='sp')
        elif self.__stg_env is not None:
            self.__select_env(type='s')
        else:
            print('no matching env combination')
            exit()
        
        self.__gitlab_diff_branch()

    def __select_env(self, type: str):
        env : str = None
        match type:
            case 'srp':
                env = self.__util.choose('[ask] choose environment?', ['stg', 'rc', 'prod'])
            case 'sp':
                env = self.__util.choose('[ask] choose environment?', ['stg', 'prod'])
            case 's':
                env = self.__util.choose('[ask] choose environment?', ['stg'])
        
        if env is None:
            print('no environment selected, terminated!')
            exit()
        
        match env:
            case 'stg':
                self.__select_env = self.__stg_env
            case 'rc':
                self.__select_env = self.__rc_env
            case 'prod':
                self.__select_env = self.__prod_env

    def __gitlab_diff_branch(self):
        print(f'call gitlab api: diff branch ({self.__selected_env.git_prev_branch} → {self.__selected_env.git_branch})')
