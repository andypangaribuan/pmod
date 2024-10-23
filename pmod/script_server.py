#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

from typing import Optional
from packaging.version import Version
from pmod.script_server_model import *
from pmod.script_server_util import *
from pmod.script_server_user_func import *


class ScripServer:
    __util                    : ScriptServerUtil = ScriptServerUtil()
    __conf                    : ScriptServerConf = None
    __stg_env                 : ScriptServerEnv  = None
    __rc_env                  : ScriptServerEnv  = None
    __prod_env                : ScriptServerEnv  = None
    __after_clone_func        : callable         = None
    __add_build_arg_func      : callable         = None
    __repository_type         : str              = None
    __selected_env            : ScriptServerEnv  = None
    __selected_env_code       : str              = None
    __workflow_env_code       : str              = None
    __current_image_version   : Version          = None
    __below_env_image_version : Version          = None
    __above_env_image_version : Version          = None
    __prefer_next_version     : Version          = None
    __user_next_version       : Version          = None


    def __init__(self, conf: ScriptServerConf, stg_env: ScriptServerEnv = None, rc_env: ScriptServerEnv = None, prod_env: ScriptServerEnv = None, after_clone_func: callable = None, add_build_arg_func: callable = None):
        self.__conf     = conf
        self.__stg_env  = stg_env
        self.__rc_env   = rc_env
        self.__prod_env = prod_env
        self.__after_clone_func = after_clone_func
        self.__add_build_arg_func = add_build_arg_func


    def run(self):
        self.__validate()
        self.__select_env()
        self.__validate_selected()
        self.__git_diff_branch()
        self.__get_current_image_version()
        self.__diff_branch_with_tag_version()
        self.__get_below_or_above_image_version()
        self.__get_user_next_version()
        self.__ask_user_next_version()
        self.__create_git_tag()
        self.__perform_git_clone()
        self.__execute_commands_before_image_build()
        self.__perform_after_clone_func()
        self.__perform_build_image()
        self.__perform_image_push()
        self.__perform_docker_prune()


    def __validate(self):
        if len(self.__conf.git_repo) > 10 and self.__conf.git_repo[:10] == 'gitlab.com':
            self.__repository_type = 'gitlab.com'
        else:
            print(f'\n🔴 only support gitlab.com repository')
            exit()

        if self.__conf.host_build_path is None:
            print(f'\n🔴 have no host_build_path configured')
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


        # VALIDATE HOSTING TYPES
        if self.__stg_env is not None and self.__stg_env.hosting_type not in ['gcp']:
            print(f'\n🔴 [stg-env] hosting type support: gcp')
            exit()

        if self.__rc_env is not None and self.__rc_env.hosting_type not in ['gcp']:
            print(f'\n🔴 [rc-env] hosting type support: gcp')
            exit()

        if self.__prod_env is not None and self.__prod_env.hosting_type not in ['gcp']:
            print(f'\n🔴 [prod-env] hosting type support: gcp')
            exit()


        # VALIDATE DEPLOYMENT TYPES
        if self.__stg_env is not None and self.__stg_env.deployment_type not in ['k8s']:
            print(f'\n🔴 [stg-env] deployment type support: k8s')
            exit()

        if self.__rc_env is not None and self.__rc_env.deployment_type not in ['k8s']:
            print(f'\n🔴 [rc-env] deployment type support: k8s')
            exit()

        if self.__prod_env is not None and self.__prod_env.deployment_type not in ['k8s']:
            print(f'\n🔴 [prod-env] deployment type support: k8s')
            exit()


        # VALIDATE IMAGE REGISTRY TYPES
        if self.__stg_env is not None and self.__stg_env.image_registry not in ['gcp-artifact-registry']:
            print(f'\n🔴 [stg-env] supported image registry: gcp-artifact-registry')
            exit()

        if self.__rc_env is not None and self.__rc_env.image_registry not in ['gcp-artifact-registry']:
            print(f'\n🔴 [rc-env] supported image registry: gcp-artifact-registry')
            exit()

        if self.__prod_env is not None and self.__prod_env.image_registry not in ['gcp-artifact-registry']:
            print(f'\n🔴 [prod-env] supported image registry: gcp-artifact-registry')
            exit()


        # VALIDATE IMAGE NAME
        if self.__stg_env is not None and self.__stg_env.image_name is None:
            print(f'\n🔴 [stg-env] image name is required')
            exit()

        if self.__rc_env is not None and self.__rc_env.image_name is None:
            print(f'\n🔴 [rc-env] image name is required')
            exit()

        if self.__prod_env is not None and self.__prod_env.image_name is None:
            print(f'\n🔴 [prod-env] image name is required')
            exit()


    def __select_env(self):
        if self.__conf.terminate_when == 'select-env':
            exit()

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


    def __validate_selected(self):
        if self.__conf.terminate_when == 'validate-selected':
            exit()

        if self.__selected_env.container_cloud_sdk is None:
            print(f'\n🔴 empty container_cloud_sdk')
            exit()


    def __git_diff_branch(self):
        if self.__conf.terminate_when == 'git-diff-branch':
            exit()

        if self.__repository_type not in ['gitlab.com']:
            print(f'\n🔴 error: unhandled logic')
            exit()

        if self.__repository_type == 'gitlab.com':
            print(f'\n→ call gitlab api: diff branch ({self.__selected_env.git_prev_branch} → {self.__selected_env.git_branch})')
            diffs, err = self.__util.gitlab_diff_branch(self.__conf, self.__selected_env.git_prev_branch, self.__selected_env.git_branch)
            if err is not None:
                print(f'🔴 error: {err}')
                exit()

            if diffs == 0:
                print(f'no changes')
            else:
                self.__util.gitlab_create_mr(self.__conf, self.__selected_env)


    def __get_current_image_version(self):
        if self.__conf.terminate_when == 'get-current-image-version':
            exit()

        current: list = None

        match self.__selected_env_code:
            case 'stg':
                current = [self.__stg_env, 'stg']
            case 'rc':
                current = [self.__rc_env, 'rc']
            case 'prod':
                current = [self.__prod_env, 'prod']

        err: str = None
        current_version: Version = None

        current_version, err = self.__util.fetch_latest_image_version(current[0], current[1])
        if err is not None:
            print(f'🔴 error: {err}')
            exit()

        self.__current_image_version = current_version


    def __get_below_or_above_image_version(self):
        if self.__conf.terminate_when == 'get-below-or-above-image-version':
            exit()

        below   : list = None
        above   : list = None

        match self.__workflow_env_code:
            case 'srp':
                match self.__selected_env_code:
                    case 'stg':
                        above = [self.__rc_env, 'rc']
                    
                    case 'rc':
                        below = [self.__stg_env, 'stg']
                    
                    case 'prod':
                        below = [self.__rc_env, 'rc']

            case 'sp':
                match self.__selected_env_code:
                    case 'stg':
                        above = [self.__prod_env, 'prod']
                        
                    case 'prod':
                        below = [self.__stg_env, 'stg']

        err                     : str     = None
        below_env_image_version : Version = None
        above_env_image_version : Version = None

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

        self.__below_env_image_version = below_env_image_version
        self.__above_env_image_version = above_env_image_version


    def __diff_branch_with_tag_version(self):
        if self.__conf.terminate_when == 'diff-branch-with-tag-version':
            exit()

        if self.__repository_type not in ['gitlab.com']:
            print(f'\n🔴 error: unhandled logic')
            exit()

        if self.__repository_type == 'gitlab.com':
            current_image_version: str = self.__util.get_version_text(self.__current_image_version)
            print(f'\n→ call gitlab api: diff (branch:{self.__selected_env.git_branch} → tag:v{current_image_version})')
            diffs, err_message = self.__util.gitlab_diff_branch(self.__conf, self.__selected_env.git_branch, f'v{current_image_version}')
            if err_message is not None:
                print(f'🔴 error: {err_message}')
                exit()

            if diffs == 0:
                print(f"no changes from branch '{self.__selected_env.git_branch}' with tag 'v{current_image_version}'")
                exit()

            print(f'have {diffs} diff, good to go')


    def __get_user_next_version(self):
        if self.__conf.terminate_when == 'get-user-next-version':
            exit()

        stg_start_version: Version = Version('1.0.0.0')
        code             : str     = f'{self.__workflow_env_code}: {self.__selected_env_code}'

        match code:
            case 's: stg':
                if self.__current_image_version is None:
                    self.__prefer_next_version = stg_start_version
                    return

                self.__prefer_next_version = self.__util.increase_version(self.__current_image_version)
                return


            case 'sp: stg' | 'srp: stg':
                if self.__current_image_version is None:
                    self.__prefer_next_version = stg_start_version
                    return

                if self.__above_env_image_version is None:
                    self.__prefer_next_version = self.__util.increase_version(self.__current_image_version)
                    return

                if self.__current_image_version.major >= self.__above_env_image_version.major:     # X._._._
                    if self.__current_image_version.minor > self.__above_env_image_version.minor:  # O.X._._
                        self.__prefer_next_version = self.__util.increase_version(self.__current_image_version)
                        return

                    if self.__current_image_version.micro > self.__above_env_image_version.micro:  # O.O.X._
                        self.__prefer_next_version = self.__util.increase_version(self.__current_image_version)
                        return

                    self.__prefer_next_version = Version(f'{self.__current_image_version.major}.{self.__current_image_version.minor}.{self.__current_image_version.micro+1}.1')
                    return



            case 'srp: rc':
                if self.__current_image_version is None and self.__below_env_image_version is None:
                    print(f'\n🔴 below version not found, expected have stg image version')
                    exit()

                if (
                        self.__current_image_version is None or
                        self.__below_env_image_version.major > self.__current_image_version.major or # X._._._
                        self.__below_env_image_version.minor > self.__current_image_version.minor or # O.X._._
                        self.__below_env_image_version.micro > self.__current_image_version.micro    # O.O.X._
                    ):
                    self.__prefer_next_version = Version(f'{self.__below_env_image_version.major}.{self.__below_env_image_version.minor}.{self.__below_env_image_version.micro}.rc1')
                    return

                self.__prefer_next_version = self.__util.increase_version(self.__current_image_version)
                return


            case 'sp: prod' | 'srp: prod':
                if self.__current_image_version is None and self.__below_env_image_version is None:
                    if self.__workflow_env_code == 'sp':
                        print(f'\n🔴 below version not found, expected have stg image version')
                    if self.__workflow_env_code == 'srp':
                        print(f'\n🔴 below version not found, expected have rc image version')
                    exit()

                if (
                    self.__current_image_version is None or
                    self.__below_env_image_version.major > self.__current_image_version.major or  # X._._._
                    self.__below_env_image_version.minor > self.__current_image_version.minor or  # O.X._._
                    self.__below_env_image_version.micro > self.__current_image_version.micro     # O.O.X._
                ):
                    self.__prefer_next_version = Version(f'{self.__below_env_image_version.major}.{self.__below_env_image_version.minor}.{self.__below_env_image_version.micro}')
                    return

                self.__prefer_next_version = self.__util.increase_version(self.__current_image_version)
                return

        if self.__prefer_next_version is None:
            print(f'\n🔴 cannot give you the preferable next version')
            exit()


    def __ask_user_next_version(self):
        if self.__conf.terminate_when == 'ask-user-next-version':
            exit()

        print(f'\n❖ preferable next version: {self.__util.get_version_text(self.__prefer_next_version)}')

        def validate_major_minor_micro(input_version: Version) -> Optional[str]:
            if input_version.major < self.__prefer_next_version.major:
                return f'🔴 major version "{input_version.major}" cannot less than prefer next version "{self.__prefer_next_version.major}"'
            
            if input_version.major > self.__prefer_next_version.major:
                return None

            if input_version.minor < self.__prefer_next_version.minor:
                return f'🔴 minor version "{input_version.minor}" cannot less than prefer next version "{self.__prefer_next_version.minor}"'
            
            if input_version.minor > self.__prefer_next_version.minor:
                return None

            if input_version.micro < self.__prefer_next_version.micro:
                return f'🔴 micro version "{input_version.micro}" cannot less than prefer next version "{self.__prefer_next_version.micro}"'

            return None

        while self.__user_next_version is None:
            err_message: str = None
            input_value = input('[ask] please input next version: ')
            input_value = input_value.strip()
            input_version, valid = self.__util.version_parse(input_value)

            if not valid:
                print('🔴 invalid version format')
                time.sleep(3)
                self.__util.remove_current_line(2)
                continue

            match self.__selected_env_code:
                case 'stg':
                    if len(input_version.release) != 4:
                        err_message = '🔴 version on staging must be using 4 part number'

                    if err_message is None:
                        err_message = validate_major_minor_micro(input_version)

                    if err_message is None:
                        _, nano_value = self.__util.get_last_index_version(input_version)
                        _, prefer_nano_value = self.__util.get_last_index_version(self.__prefer_next_version)
                        if nano_value < prefer_nano_value:
                            err_message = f'🔴 nano version "{nano_value}" cannot less than prefer next version "{prefer_nano_value}"'

                case 'rc':
                    if len(input_version.release) != 3 or input_version.pre is None:
                        err_message = '🔴 version on rc must be using 3 part number and rc-number'

                    if err_message is None:
                        err_message = validate_major_minor_micro(input_version)

                    if err_message is None and input_version.pre[0] != 'rc':
                        err_message = '🔴 mush have "rc" part'

                    if err_message is None and input_version.pre[1] < self.__prefer_next_version.pre[1]:
                        err_message = f'🔴 rc version "{input_version.pre[1]}" cannot less than prefer next version "{self.__prefer_next_version.pre[1]}"'

                case 'prod':
                    if len(input_version.release) != 3 or f'{input_version.major}.{input_version.minor}.{input_version.micro}' != input_version.public:
                        err_message = '🔴 version on prod must be using 3 part number'

                    if err_message is None:
                        err_message= validate_major_minor_micro(input_version)

            if err_message is not None:
                print(err_message)
                time.sleep(6)
                self.__util.remove_current_line(2)
                continue

            if self.__prefer_next_version is not None and input_version.public != self.__prefer_next_version.public:
                print('[ask] preferable next version and yours is not same, continue? (yes, no or cancel)')
                while True:
                    input_value = input()

                    match input_value:
                        case 'yes' | 'y':
                            self.__user_next_version = input_version
                            break

                        case 'no' | 'n':
                            exit()

                        case 'cancel' | 'c':
                            self.__util.remove_current_line(3)
                            break

                    self.__util.remove_current_line()
            else:
                self.__user_next_version = input_version


    def __create_git_tag(self):
        if self.__conf.terminate_when == 'create-git-tag':
            exit()

        if self.__repository_type not in ['gitlab.com']:
            print(f'\n🔴 error: unhandled logic')
            exit()

        version: str = f'v{self.__util.get_version_text(self.__user_next_version)}'

        if self.__repository_type == 'gitlab.com':
            print('\n→ find tag on gitlab')
            tag_exists, err_message = self.__util.gitlab_find_tag(self.__conf, self.__user_next_version)
            if err_message is not None:
                print(f'\n🔴 error: {err_message}')
                exit()

            if tag_exists:
                print(f'tag {version} already exists')
                print('\n→ delete the existing tag')
                err_message = self.__util.gitlab_delete_tag(self.__conf, self.__user_next_version)
                if err_message is not None:
                    print(f'\n🔴 error: {err_message}')
                    exit()
            else:
                print(f'tag {version} not exists')

            print(f'\n→ create git tag {version} from branch {self.__selected_env.git_branch}')
            err_message = self.__util.gitlab_create_tag(self.__conf, self.__user_next_version, self.__selected_env.git_branch)
            if err_message is not None:
                print(f'\n🔴 error: {err_message}')
                exit()


    def __perform_git_clone(self):
        if self.__conf.terminate_when == 'perform-git-clone':
            exit()

        err_message = self.__util.git_clone(self.__conf, self.__user_next_version, self.__repository_type)
        if err_message is not None:
            print(f'\n🔴 error: {err_message}')
            exit()


    def __execute_commands_before_image_build(self):
        if self.__conf.terminate_when == 'execute-commands-before-image-build':
            exit()

        if len(self.__conf.cmds_before_build) == 0:
            return

        print(f'\n❖ perform commands before image build')
        err_message = self.__util.execute_command_before_image_build(self.__conf)
        if err_message is not None:
            print(f'\n🔴 error: {err_message}')
            exit()


    def __perform_after_clone_func(self):
        if self.__conf.terminate_when == 'perform-after-clone-func':
            exit()

        if self.__after_clone_func is None:
            return

        print('\n→ perform after clone func')
        user_func = ScriptServerUserFunc(self.__conf, self.__selected_env_code)
        self.__after_clone_func(user_func)


    def __perform_build_image(self):
        if self.__conf.terminate_when == 'perform-build-image':
            exit()

        print('\n❖ perform build image')
        add_build_arg: str = None
        if self.__add_build_arg_func is not None:
            add_build_arg = self.__add_build_arg_func(self.__selected_env_code, self.__util.get_version_text(self.__user_next_version))

        err_message = self.__util.build_image(self.__conf, self.__selected_env, self.__user_next_version, add_build_arg)
        if err_message is not None:
            print(f'\n🔴 error: {err_message}')
            exit()


    def __perform_image_push(self):
        if self.__conf.terminate_when == 'perform-image-push':
            exit()

        print('\n→ perform image push')
        err_message = self.__util.push_image(self.__selected_env, self.__user_next_version)
        if err_message is not None:
            print(f'\n🔴 error: {err_message}')
            exit()


    def __perform_docker_prune(self):
        if self.__conf.terminate_when == 'perform-docker-prune':
            exit()

        if self.__conf.do_docker_prune:
            print('\n→ perform docker prune')

