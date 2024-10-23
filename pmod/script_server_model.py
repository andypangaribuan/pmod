#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

class ScriptServerConf:
    image_name        : str       = None
    project_name      : str       = None
    timezone          : str       = None
    git_repo          : str       = None
    git_id            : str       = None
    git_user          : str       = None
    git_pass          : str       = None
    dockerfile_path   : str       = None
    do_docker_prune   : bool      = False
    host_build_path   : str       = None
    cmds_before_build : list[str] = []
    terminate_when    : str       = None


class ScriptServerEnv:
    timezone                          : str = None
    hosting_type                      : str = None  # types: gcp
    deployment_type                   : str = None  # types: k8s
    image_registry                    : str = None  # types: gcp-artifact-registry
    gcp_artifact_registry_location    : str = None
    gcp_artifact_registry_repository  : str = None
    gcp_artifact_registry_package     : str = None
    container_cloud_sdk               : str = None  # only for hosting_type = gcp
    git_prev_branch                   : str = None
    git_branch                        : str = None
    image_name                        : str = None
    image_namespace                   : str = None  # required if deployment_type=k8s
