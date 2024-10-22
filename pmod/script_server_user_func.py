#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

import os
from typing import Optional
from pmod.script_server_model import *


class ScriptServerUserFunc:
    __conf           : ScriptServerConf = None
    selected_env_code: str              = None


    def __init__(self, conf: ScriptServerConf, selected_env_code: str):
        self.__conf = conf
        self.selected_env_code = selected_env_code


    def execute_command(self, command: str) -> Optional[str]:
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'cd %s; %s'
        cmd = cmd % (self.__conf.host_build_path, command)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code} from command "{command}"'
        return None


    def write_file(self, file_path: str, content: str) -> Optional[str]:
        host_file_path = f'{self.__conf.host_build_path}/{file_path}'

        try:
            with open(host_file_path, 'w+') as file:
                try:
                    file.write(content)
                except Exception:
                    return f'failed when writing to the file\nfile: {file_path}\ncontent: {content}'
        except Exception:
            return f'failed when open the file {file_path}'

        return None

