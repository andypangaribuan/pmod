#
# Copyright (c) 2024.
# Created by Andy Pangaribuan <https://github.com/apangaribuan>.
#
# This product is protected by copyright and distributed under
# licenses restricting copying, distribution and decompilation.
# All Rights Reserved.
#

class ScriptServerConf:
    project_name   : str = None
    timezone       : str = None
    git_repo       : str = None
    git_id         : str = None
    git_user       : str = None
    git_pass       : str = None
    dockerfile_path: str = None


class ScriptServerEnv:
    timezone           : str = None
    hosting_type       : str = None  # types: gcp
    deployment_type    : str = None  # types: k8s
    container_cloud_sdk: str = None  # only for hosting_type = gcp
    git_prev_branch    : str = None
    git_branch         : str = None