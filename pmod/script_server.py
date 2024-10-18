#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

class ScriptServerConf:
    project_name: str = None
    timezone: str = None
    git_type: str = None # types: gitlab
    git_repo: str = None
    git_id: str = None
    git_user: str = None
    git_pass: str = None


class ScriptServerEnv:
    env_name       : str = None
    timezone       : str = None
    hosting_type   : str = None # types: gcp
    deployment_type: str = None # types: k8s
    gcp_project_name: str = None  # only for hosting_type=gcp


class ScripServer:
    __conf: ScriptServerConf = None
    __stg_env: ScriptServerEnv = None
    __rc_env: ScriptServerEnv = None
    __prod_env: ScriptServerEnv = None

    def __init__(self, conf: ScriptServerConf, stg_env: ScriptServerEnv, rc_env: ScriptServerEnv, prod_env: ScriptServerEnv):
        self.__conf = conf
        self.__stg_env = stg_env
        self.__rc_env = rc_env
        self.__prod_env = prod_env
