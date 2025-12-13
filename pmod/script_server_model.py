'''
Copyright (c) 2025.
Created by Andy Pangaribuan (iam.pangaribuan@gmail.com)
https://github.com/apangaribuan

This product is protected by copyright and distributed under
licenses restricting copying, distribution and decompilation.
All Rights Reserved.
'''


class ScriptServerConf:
    timezone         : str | None  = None
    git_repo         : str | None  = None
    git_id           : str | None  = None
    git_user         : str | None  = None
    git_pass         : str | None  = None
    git_project_path : str | None  = None   # optional, project path in sub directory, e.g. value: service/middleware
    git_tag_prefix   : str | None  = None   # optional, e.g. value: -middleware,       result: v1.2.3-middleware
    dockerfile_path  : str | None  = None
    do_docker_prune  : bool | None = False
    host_build_path  : str | None  = None
    cmds_before_build: list[str]   = []
    terminate_when   : str | None  = None


class ScriptServerEnv:
    name                            : str | None = None
    hosting_type                    : str | None = None  # types: gcp, vm
    deployment_type                 : str | None = None  # types: k8s, docker
    image_registry                  : str | None = None  # types: gcp-artifact-registry
    gcp_artifact_registry_location  : str | None = None
    gcp_artifact_registry_repository: str | None = None
    gcp_artifact_registry_package   : str | None = None
    container_cloud_sdk             : str | None = None  # only for hosting_type       = gcp
    git_prev_branch                 : str | None = None
    git_branch                      : str | None = None
    image_name                      : str | None = None
    image_namespace                 : str | None = None  # required if deployment_type = k8s
    k8s_deployment_name             : str | None = None  # required if deployment_type = k8s
    vm_ip_address                   : str | None = None  # required if deployment_type = vm
    vm_username                     : str | None = None  # required if deployment_type = vm
    vm_ssh_key_path                 : str | None = None  # required if deployment_type = vm
    cmds_before_build               : list[str]  = []
