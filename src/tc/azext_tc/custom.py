# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import sleep
from urllib.parse import urlparse
from knack.util import CLIError
from knack.log import get_logger
from azext_tc.vendored_sdks.teamcloud.models import (
    StatusResult,
    ProjectDefinition,
    UserDefinition,
    Provider,
    ProjectType)

logger = get_logger(__name__)

STATUS_POLLING_SLEEP_INTERVAL = 2

# pylint: disable=unused-argument, protected-access


# ----------------
# TeamCloud
# ----------------

def teamcloud_create(cmd, client, base_url, config_yaml):
    client._client.config.base_url = base_url
    raise CLIError('TODO: Implement `az tc create`')


def status_get(cmd, client, base_url, tracking_id, project=None):
    client._client.config.base_url = base_url
    return client.get_project_status(project, tracking_id) if project else client.get_status(tracking_id)


# ----------------
# TeamCloud Users
# ----------------

def teamcloud_user_create(cmd, client, base_url, user_name, user_role='Creator', tags=None):
    user_definition = UserDefinition(
        email=user_name, role=user_role, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=user_definition,
                               create_func=client.create_team_cloud_user,
                               get_func=client.get_team_cloud_user_by_name_or_id)


def teamcloud_user_delete(cmd, client, base_url, user):
    return _delete_with_status(cmd, client, base_url, user, client.delete_team_cloud_user)


def teamcloud_user_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_team_cloud_users()


def teamcloud_user_get(cmd, client, base_url, user):
    client._client.config.base_url = base_url
    return client.get_team_cloud_user_by_name_or_id(user)

# ----------------
# Projects
# ----------------


def project_create(cmd, client, base_url, project_name, project_type=None, tags=None):
    project_definition = ProjectDefinition(
        name=project_name, project_type=project_type, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=project_definition,
                               create_func=client.create_project,
                               get_func=client.get_project_by_name_or_id)


def project_delete(cmd, client, base_url, project):
    return _delete_with_status(cmd, client, base_url, project, client.delete_project)


def project_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_projects()


def project_get(cmd, client, base_url, project):
    client._client.config.base_url = base_url
    return client.get_project_by_name_or_id(project)


# ----------------
# Project Users
# ----------------

def project_user_create(cmd, client, base_url, project, user_name, user_role='Member', tags=None):
    user_definition = UserDefinition(
        email=user_name, role=user_role, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=user_definition,
                               create_func=client.create_project_user,
                               get_func=client.get_project_user_by_name_or_id,
                               project_id=project)


def project_user_delete(cmd, client, base_url, project, user):
    return _delete_with_status(cmd, client, base_url, user, client.delete_project_user, project)


def project_user_list(cmd, client, base_url, project):
    client._client.config.base_url = base_url
    return client.get_project_users(project)


def project_user_get(cmd, client, base_url, project, user):
    client._client.config.base_url = base_url
    return client.get_project_user_by_name_or_id(user, project)


# ----------------
# Project Types
# ----------------

def project_type_create(cmd, client, base_url, project_type, tags=None):
    client._client.config.base_url = base_url
    proj_type = ProjectType(id=project_type, tags=tags)
    return client.create_project_type(proj_type)


def project_type_delete(cmd, client, base_url, project_type):
    client._client.config.base_url = base_url
    return client.delete_project_type(project_type)


def project_type_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_project_types()


def project_type_get(cmd, client, base_url, project_type):
    client._client.config.base_url = base_url
    return client.get_project_type_by_id(project_type)


# ----------------
# Providers
# ----------------

def provider_create(cmd, client, base_url, provider):
    payload = Provider(provider)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=payload,
                               create_func=client.create_provider,
                               get_func=client.get_provider_by_id)


def provider_delete(cmd, client, base_url, provider):
    return _delete_with_status(cmd, client, base_url, provider, client.delete_provider)


def provider_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_providers()


def provider_get(cmd, client, base_url, provider):
    client._client.config.base_url = base_url
    return client.get_provider_by_id(provider)


# ----------------
# Util
# ----------------

def _create_with_status(cmd, client, base_url, payload, create_func, get_func, project_id=None):
    client._client.config.base_url = base_url

    type_name = create_func.metadata['url'].split('/')[-1][:-1].capitalize()

    hook = cmd.cli_ctx.get_progress_controller()

    hook.add(message='Starting: Creating new {}'.format(type_name))

    result = create_func(
        project_id, payload) if project_id else create_func(payload)

    while isinstance(result, StatusResult):
        if result.code == 200:
            hook.end(messag='Finished.')
            return result

        if result.code == 202:
            for _ in range(STATUS_POLLING_SLEEP_INTERVAL * 2):
                hook.add(message='{}: {}'.format(
                    result.state, result.state_message or 'Creating new {}'.format(type_name)))
                sleep(0.5)

            # status for project children
            if project_id:
                result = client.get_project_status(
                    project_id, result._tracking_id)
            # status for project
            elif 'projects' in result.location:
                paths = urlparse(result.location).path.split('/')
                p_id = paths[paths.index('projects') + 1]
                result = client.get_project_status(p_id, result._tracking_id)
            # status for teamcloud children
            else:
                result = client.get_status(result._tracking_id)

    hook.end(messag='Finished.')

    return result


def _delete_with_status(cmd, client, base_url, item_id, delete_func, project_id=None):
    client._client.config.base_url = base_url

    type_name = delete_func.metadata['url'].split('/')[-2][:-1].capitalize()

    hook = cmd.cli_ctx.get_progress_controller()

    hook.add(message='Starting: Delete {}'.format(type_name))

    result = delete_func(
        project_id, item_id) if project_id else delete_func(item_id)

    while isinstance(result, StatusResult):
        if result.code == 200:
            hook.end(messag='Finished.')
            return result

        if result.code == 202:
            for _ in range(STATUS_POLLING_SLEEP_INTERVAL * 2):
                hook.add(message='{}: {}'.format(
                    result.state, result.state_message or 'Deleting {}'.format(type_name)))
                sleep(0.5)

            # status for project children
            if project_id:
                result = client.get_project_status(
                    project_id, result._tracking_id)
            # status for project
            elif 'projects' in result.location:
                paths = urlparse(result.location).path.split('/')
                p_id = paths[paths.index('projects') + 1]
                result = client.get_project_status(p_id, result._tracking_id)
            # status for teamcloud children
            else:
                result = client.get_status(result._tracking_id)

    hook.end(messag='Finished.')

    return result
