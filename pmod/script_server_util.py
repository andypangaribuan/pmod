'''
Copyright (c) 2025.
Created by Andy Pangaribuan (iam.pangaribuan@gmail.com)
https://github.com/apangaribuan

This product is protected by copyright and distributed under
licenses restricting copying, distribution and decompilation.
All Rights Reserved.
'''

import os
import time
import requests
import subprocess
import re
from typing import Any, Optional
from tabulate import tabulate
from packaging.version import Version
from pmod.script_server_model import ScriptServerConf, ScriptServerEnv


class ScriptServerUtil:
    def sh_get(self, cmd: str) -> tuple[str, str]:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return process.communicate()

    def join_words(self, items: list[str], unionSeparator: str = ',', lastSeparator: str = 'and') -> str:
        if len(items) > 2:
            return '%s %s %s' % (f'{unionSeparator} '.join(items[:-1]), lastSeparator, items[-1])
        else:
            return f' {lastSeparator} '.join(items)

    def version_parse(self, ver: str) -> tuple[Version | None, bool]:
        try:
            v = Version(ver)
            return v, True
        except Exception:
            return None, False

    def choose(self, message: str, items: list[str]) -> str:
        print(f'{message} ({self.join_words(items, lastSeparator="or")})')
        selected: str | None = None
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

    def dict_value(self, dictionary, keys: list[str]) -> Optional[Any]:
        value = None
        nested_dict = dictionary

        for key in keys:
            try:
                nested_dict = nested_dict[key]
                value = nested_dict
            except KeyError:
                return None

        return value

    def get_version_text(self, ver: Version | None) -> str:
        if ver is None:
            return ''
        if ver.pre is not None:
            return f'{ver.major}.{ver.minor}.{ver.micro}.{ver.pre[0]}{ver.pre[1]}'
        return ver.public

    def gitlab_diff_branch(self, conf: ScriptServerConf, branch_from: str, branch_to: str) -> tuple[Optional[int], Optional[str]]:
        if conf.git_pass is None:
            return None, 'git_pass is required'

        url: str = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/compare?from={branch_from}&to={branch_to}&straight=true'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return None, f'http code: {res.status_code}'

        diffs = self.dict_value(res.json(), ['diffs'])
        if diffs is None:
            return None, 'diffs not found'

        return len(diffs), None

    def gitlab_create_mr(self, conf: ScriptServerConf, selected_env: ScriptServerEnv):
        mr_url = f'https://{conf.git_repo}/-/merge_requests/new?merge_request'
        source = f'source_project_id%5D={conf.git_id}&merge_request%5Bsource_branch%5D={selected_env.git_prev_branch}'
        target = f'target_project_id%5D={conf.git_id}&merge_request%5Btarget_branch%5D={selected_env.git_branch}'
        url = f'{mr_url}%5B{source}&merge_request%5B{target}'

        print(f"have new files from branch '{selected_env.git_prev_branch}' to branch '{selected_env.git_branch}'")
        print('🟠 please do manual MR')
        print(f'url: {url}')
        exit()

    def gitlab_find_tag(self, conf: ScriptServerConf, tag_name: str) -> tuple[bool, str | None]:
        if conf.git_pass is None:
            return False, 'git_pass is required'

        url: str = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/tags/{tag_name}'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.get(url, headers=headers)
        jons = res.json()

        match res.status_code:
            case 404:
                message = self.dict_value(jons, ['message'])
                if message == '404 Tag Not Found':
                    return False, None

            case 200:
                name = self.dict_value(jons, ['name'])
                if name == tag_name:
                    return True, None

        return False, f'http code: {res.status_code}\nresponse: {jons}'

    def gitlab_delete_tag(self, conf: ScriptServerConf, tag_name: str) -> Optional[str]:
        if conf.git_pass is None:
            return 'git_pass is required'

        url = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/tags/{tag_name}'
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

    def gitlab_create_tag(self, conf: ScriptServerConf, tag_name: str, branch: str) -> Optional[str]:
        if conf.git_pass is None:
            return 'git_pass is required'

        url = f'https://gitlab.com/api/v4/projects/{conf.git_id}/repository/tags?tag_name={tag_name}&ref={branch}'
        headers: dict[str, str] = {'PRIVATE-TOKEN': conf.git_pass}
        res = requests.post(url, headers=headers)
        if res.status_code not in [200, 201]:
            return f'http code: {res.status_code}, response: {res.json()}'

        try:
            version_name = self.dict_value(res.json(), ['name'])
            if version_name == tag_name:
                return None
            return f'http code: {res.status_code}, response: {res.json()}'
        except Exception:
            return f'invalid output: {res.json()}'

    def get_last_index_version(self, ver: Version) -> tuple[int, int]:
        last_index = len(ver.release) - 1
        return last_index, ver.release[last_index]

    def increase_version(self, ver: Version) -> Version:
        if ver.pre is None:
            last_index, value = self.get_last_index_version(ver)
            ls = [str(v) for v in ver.release]
            ls[last_index] = str(value + 1)
            return Version('.'.join(ls))

        pre_name, pre_ver = ver.pre
        ls = [str(v) for v in ver.release]
        new_version = '.'.join(ls)
        return Version(f'{new_version}.{pre_name}{pre_ver + 1}')

    def fetch_latest_image_version(self, env: ScriptServerEnv, env_name: str) -> tuple[Version | None, str | None]:
        if env.image_registry not in ['gcp-artifact-registry']:
            return None, 'unhandled logic'

        if env.image_registry == 'gcp-artifact-registry':
            print(f'\n→ call gcloud api: get image last version on {env_name}')

            cmd: str = 'chroot /hostfs /bin/bash -c "docker exec -it %s %s"'
            cmd = cmd % (env.container_cloud_sdk, 'gcloud artifacts tags list --location=%s --repository=%s --package=%s --format=\'table(TAG)\'')
            cmd = cmd % (env.gcp_artifact_registry_location, env.gcp_artifact_registry_repository, env.gcp_artifact_registry_package)

            out, err = self.sh_get(cmd)
            if err != "":
                print(f'🔴 error: {err}')
                return None, err
            if 'TAG' not in out:
                print('have no image version')
                return None, f'TAG not found in {out}'

            lines = out.splitlines()
            image_version: Version | None = None

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

            print(f'{image_version}')
            return image_version, None

        return None, 'image version not found'

    def git_clone(self, conf: ScriptServerConf, tag_name: str, repository_type: str) -> Optional[str]:
        if repository_type not in ['gitlab.com']:
            return 'unhandled logic'

        host_build_path = f'/hostfs{conf.host_build_path}'

        print('\n→ clean the build directory')
        cmd = 'rm -rf %s; mkdir -p %s'
        cmd = cmd % (host_build_path, host_build_path)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'

        print(f'\n→ clone the git project, tag: {tag_name}')
        cmd = 'cd %s; git clone --quiet -c advice.detachedHead=false --depth 1 --branch %s https://%s:%s@%s.git .'
        cmd = cmd % (host_build_path, tag_name, conf.git_user, conf.git_pass, conf.git_repo)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'

        if conf.git_project_path is not None:
            print('\n→ prepare project directory')
            cmd = cmd % "cd %s; mv %s .___; find . -maxdepth 1 ! -name '.' ! -name '.___'  -exec rm -rf {} +; mv .___/{.,}* .; rm -rf .___"
            cmd = cmd % (host_build_path, conf.git_project_path)
            err_code = os.system(cmd)
            if err_code != 0:
                return f'os error code {err_code}'

    def execute_command_before_image_build(self, conf: ScriptServerConf, selected_env: ScriptServerEnv) -> Optional[str]:
        for i in range(len(conf.cmds_before_build)):
            print(f'- execute command {i + 1}/{len(conf.cmds_before_build)}')

            cmd = 'chroot /hostfs /bin/bash -c "%s"'
            cmd = cmd % 'cd %s; %s'
            cmd = cmd % (conf.host_build_path, conf.cmds_before_build[i])
            err_code = os.system(cmd)
            if err_code != 0:
                return f'os error code {err_code} from command "{conf.cmds_before_build[i]}"'

        for i in range(len(selected_env.cmds_before_build)):
            print(f'- execute command {i + 1}/{len(selected_env.cmds_before_build)}')

            cmd = 'chroot /hostfs /bin/bash -c "%s"'
            cmd = cmd % 'cd %s; %s'
            cmd = cmd % (conf.host_build_path, selected_env.cmds_before_build[i])
            err_code = os.system(cmd)
            if err_code != 0:
                return f'os error code {err_code} from command "{selected_env.cmds_before_build[i]}"'

        return None

    def docker_resolve(self) -> Optional[str]:
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'docker buildx version'
        out, err_message = self.sh_get(cmd)
        if err_message != "":
            return err_message

        if out.strip() == "":
            return 'docker buildx is not available, please install docker buildx'

        if not out.strip().startswith('github.com/docker/buildx'):
            return 'docker buildx is not available, please install docker buildx'

        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'docker buildx inspect'
        out, err_message = self.sh_get(cmd)
        if err_message != "":
            return err_message

        if out.strip() == "":
            return 'docker buildx inspect failed, please check your docker buildx installation'

        lines = out.splitlines()
        if len(lines) == 0 or not lines[0].startswith('Name:'):
            return 'docker buildx inspect returned empty output, please check your docker buildx installation'

        builder_name = lines[0].replace("Name:", "").strip()
        if builder_name == 'default':
            cmd = 'chroot /hostfs /bin/bash -c "%s"'
            cmd = cmd % 'docker buildx create --name script-server-builder --use'
            out, err_message = self.sh_get(cmd)
            if err_message != "":
                return err_message

        return None

    def build_image(self, conf: ScriptServerConf, selected_env: ScriptServerEnv, ver: Version, add_build_arg: str | None) -> Optional[str]:
        err_message = self.resolve_nameserver()
        if err_message is not None:
            return err_message

        if selected_env.image_name is None:
            return 'image_name is not set in the selected environment'

        version: str = self.get_version_text(ver)

        print('\n→ checking image on local device')
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % "docker images %s:%s | awk 'NR>1'"
        cmd = cmd % (selected_env.image_name, version)
        out, err_message = self.sh_get(cmd)
        if err_message != "":
            return err_message

        if selected_env.image_name not in out:
            print('have no image')
        else:
            print('found existing image')

        if selected_env.image_name in out:
            print('\n→ delete existing image on local device')
            cmd = 'chroot /hostfs /bin/bash -c "%s"'
            cmd = cmd % 'docker rmi %s:%s'
            cmd = cmd % (selected_env.image_name, version)
            err_code = os.system(cmd)
            if err_code != 0:
                return f'os error code {err_code}'

        print('\n→ build image on local device')
        # cmd_build_1 = 'docker build --no-cache -f %s --build-arg APP_VERSION=%s --build-arg TZ=%s -t %s .'
        # cmd_build_2 = 'docker build --no-cache -f %s --build-arg APP_VERSION=%s --build-arg TZ=%s %s -t %s .'
        cmd_build_1 = 'docker buildx build --no-cache -f %s --build-arg APP_VERSION=%s --build-arg TZ=%s -t %s --load .'
        cmd_build_2 = 'docker buildx build --no-cache -f %s --build-arg APP_VERSION=%s --build-arg TZ=%s %s -t %s --load .'
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'cd %s; %s'

        if add_build_arg is None:
            cmd = cmd % (conf.host_build_path, cmd_build_1)
            cmd = cmd % (conf.dockerfile_path, version, conf.timezone, f'{selected_env.image_name}:{version}')
        else:
            cmd = cmd % (conf.host_build_path, cmd_build_2)
            cmd = cmd % (conf.dockerfile_path, version, conf.timezone, add_build_arg, f'{selected_env.image_name}:{version}')

        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        print('\n⠀')

        return None

    def push_image(self, selected_env: ScriptServerEnv, ver: Version) -> Optional[str]:
        version: str = self.get_version_text(ver)
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'docker exec -it %s docker push %s:%s'
        cmd = cmd % (selected_env.container_cloud_sdk, selected_env.image_name, version)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def get_file_path_zip_docker_image(self, conf: ScriptServerConf, selected_env: ScriptServerEnv, ver: Version) -> str:
        if selected_env.image_name is None:
            return 'image_name is not set in the selected environment'

        version: str = self.get_version_text(ver)
        zip_file: str = f'{conf.host_build_path}/{selected_env.image_name.replace("/", "_")}_{version}.tar.gz'
        return zip_file

    def zip_docker_image(self, conf: ScriptServerConf, selected_env: ScriptServerEnv, ver: Version) -> Optional[str]:
        version: str = self.get_version_text(ver)
        image: str = f'{selected_env.image_name}:{version}'
        zip_file: str = self.get_file_path_zip_docker_image(conf, selected_env, ver)

        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'docker save %s | gzip > %s'
        cmd = cmd % (image, zip_file)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def push_image_to_vm_and_extract(self, conf: ScriptServerConf, selected_env: ScriptServerEnv, ver: Version) -> Optional[str]:
        zip_file: str = f'/hostfs{self.get_file_path_zip_docker_image(conf, selected_env, ver)}'
        cmd = 'scp -o StrictHostKeyChecking=no -i %s %s %s@%s:~/%s'
        cmd = cmd % (selected_env.vm_ssh_key_path, zip_file, selected_env.vm_username, selected_env.vm_ip_address, os.path.basename(zip_file))
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'

        cmd = 'ssh -o StrictHostKeyChecking=no -i %s %s@%s "gunzip -c ~/%s | docker load"'
        cmd = cmd % (selected_env.vm_ssh_key_path, selected_env.vm_username, selected_env.vm_ip_address, os.path.basename(zip_file))
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'

        cmd = 'ssh -o StrictHostKeyChecking=no -i %s %s@%s "rm -rf %s"'
        cmd = cmd % (selected_env.vm_ssh_key_path, selected_env.vm_username, selected_env.vm_ip_address, os.path.basename(zip_file))
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def resolve_nameserver(self) -> Optional[str]:
        '''
        IF HAVE ERROR LIKE 
            ERROR: failed to solve: composer:2.3: failed to authorize: failed to fetch anonymous token
            dial tcp: lookup auth.docker.io on 127.0.0.53:53: read udp 127.0.0.1:57682->127.0.0.53:53: read: connection refused
        THEN EDIT THE /etc/resolv.conf or /run/systemd/resolve/stub-resolv.conf
        ADD/UPDATE THIS LINE:
        nameserver 1.1.1.1
        '''
        file_path = '/hostfs/etc/resolv.conf'
        lines: list[str] = []

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
        except Exception:
            return f'something went wrong when read the file {file_path}'

        ns = 'nameserver 1.1.1.1'
        rewrite: bool = True

        for line in lines:
            line = re.sub(' +', ' ', line)
            if line == ns or line == f'{ns}\n':
                rewrite = False
                break

        if rewrite:
            print('\n→ perform resolve nameserver')
            lines.append(f'\n{ns}\n⠀')
            try:
                with open(file_path, 'w') as file:
                    try:
                        file.writelines(lines)
                    except Exception:
                        return f'failed when write the file\nfile: {file_path}\ncontent:\n{"".join(lines)}'
            except Exception:
                return f'failed when open to write the file\nfile: {file_path}'

        return None

    def delete_image(self, selected_env: ScriptServerEnv, ver: Version) -> Optional[str]:
        version: str = self.get_version_text(ver)
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'docker rmi %s:%s'
        cmd = cmd % (selected_env.image_name, version)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def delete_build_directory(self, conf: ScriptServerConf) -> Optional[str]:
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'rm -rf %s'
        cmd = cmd % (conf.host_build_path)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def docker_prune(self) -> Optional[str]:
        cmd = 'chroot /hostfs /bin/bash -c "%s"'
        cmd = cmd % 'docker container prune -f; docker image prune -f; docker builder prune -f'
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def deploy_on_gcp_k8s(self, selected_env: ScriptServerEnv, ver: Version) -> Optional[str]:
        if selected_env.container_cloud_sdk is None:
            return 'container_cloud_sdk is not set in the selected environment'

        image: str = f'{selected_env.image_name}:{self.get_version_text(ver)}'
        cmd_base = 'chroot /hostfs /bin/bash -c "docker exec -it %s"'
        cmd_base = cmd_base % (selected_env.container_cloud_sdk + ' %s')
        cmd = cmd_base % ('kubectl set image -n {ns} deployment/{dep} {dep}={img}')
        cmd = cmd.format(ns=selected_env.image_namespace, dep=selected_env.k8s_deployment_name, img=image)
        err_code = os.system(cmd)
        if err_code != 0:
            return f'os error code {err_code}'
        return None

    def wait_rolling_update_on_gcp_k8s(self, selected_env: ScriptServerEnv, targetVersion: Version):
        if selected_env.container_cloud_sdk is None:
            return 'container_cloud_sdk is not set in the selected environment'

        if selected_env.image_name is None:
            return 'image_name is not set in the selected environment'

        image_version: str = self.get_version_text(targetVersion)
        delete_lines: int = 0
        do_loop: bool = True
        headers: list[str] = ['POD', 'VERSION', 'PHASE']
        last_printed_output: str = ''

        cmd_base = 'chroot /hostfs /bin/bash -c "docker exec -it %s"'
        cmd_base = cmd_base % (selected_env.container_cloud_sdk + ' %s')

        while do_loop:
            cmd = cmd_base % 'kubectl get pods -n %s -l app=%s -o jsonpath=\'{range .items[*]}{.metadata.name} {..containers..image} {@.status.phase}|{end}\''
            cmd = cmd % (selected_env.image_namespace, selected_env.k8s_deployment_name)
            out, err = self.sh_get(cmd)
            if err != '':
                if delete_lines > 0:
                    self.remove_current_line(delete_lines)
                    delete_lines = 0

                msg = f'🔴 error when get pods: {err.strip()}'
                delete_lines = len(msg.split('\n'))
                print(msg)
                last_printed_output = ''
                time.sleep(3)
                continue

            rows: list[list] = []
            vers: list[str] = []
            lines: list[str] = out.split('\n')
            had_error: bool = False

            for line in lines:
                line = line.strip()
                ls: list[str] = line.split('|')
                if line == '':
                    continue

                for line in ls:
                    line = line.strip()
                    if line == '':
                        continue

                    items = line.split(' ')
                    if len(items) < 3:
                        had_error = True
                        break

                    name: str = ''
                    ver: str = ''
                    phase: str = ''

                    for i in range(len(items)):
                        if i == 0:
                            name = items[i]
                            continue

                        if i + 1 == len(items):
                            phase = items[i]
                            continue

                        if selected_env.image_name in items[i]:
                            ver = items[i].split(':')[1]

                    if name != '' and ver != '' and phase != '':
                        row = [name, ver, phase]
                        rows.append(row)
                        vers.append(ver)

                if had_error:
                    break

            if had_error:
                if delete_lines > 0:
                    self.remove_current_line(delete_lines)
                    delete_lines = 0

                msg = f'🔴 error when parsing the output command\n{out}'
                msg = msg.strip()
                delete_lines = len(msg.split('\n'))
                print(msg)
                last_printed_output = ''
                continue

            if len(rows) == 0:
                if delete_lines > 0:
                    self.remove_current_line(delete_lines)
                    delete_lines = 0

                msg = f'🔴 doesn\'t have any pod, output: "{out}"'
                msg = msg.strip()
                delete_lines = len(msg.split('\n'))
                print(msg)
                last_printed_output = ''
                continue

            if len(rows) > 0:
                if last_printed_output != out:
                    last_printed_output = out
                    if delete_lines > 0:
                        self.remove_current_line(delete_lines)
                        delete_lines = 0

                    delete_lines = 2 + len(rows)
                    print(tabulate(rows, headers=headers))
                    time.sleep(1)

            if len(vers) > 0:
                ls_ver = list(set(vers))
                if len(ls_ver) == 1:
                    if ls_ver[0] == image_version:
                        do_loop = False
