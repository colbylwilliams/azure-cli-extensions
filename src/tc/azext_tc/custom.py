# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import sleep
from knack.util import CLIError
from knack.log import get_logger
from urllib.parse import urlparse
from azext_tc.vendored_sdks.teamcloud.models import (
    StatusResult,
    ProjectDefinition,
    UserDefinition,
    Provider,
    ProjectType)

import urllib3
urllib3.disable_warnings()

logger = get_logger(__name__)

STATUS_POLLING_SLEEP_INTERVAL = 4

# pylint: disable=unused-argument, protected-access, logging-format-interpolation

# ----------------
# TeamCloud Users
# ----------------


def teamcloud_user_create(cmd, client, base_url, user_name, user_role, tags=None):
    user_definition = UserDefinition(
        email=user_name, role=user_role, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=user_definition,
                               create_func=client.create_team_cloud_user,
                               get_func=client.get_team_cloud_user_by_id)


def teamcloud_user_delete(cmd, client, base_url, user_id):
    return _delete_with_status(cmd, client, base_url, user_id, client.delete_team_cloud_user)


def teamcloud_user_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_team_cloud_users()


def teamcloud_user_get(cmd, client, base_url, user_id):
    client._client.config.base_url = base_url
    return client.get_team_cloud_user_by_id(user_id)


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
                               get_func=client.get_project_by_id)


def project_delete(cmd, client, base_url, project_id):
    return _delete_with_status(cmd, client, base_url, project_id, client.delete_project_user)


def project_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_projects()


def project_get(cmd, client, base_url, project_id):
    client._client.config.base_url = base_url
    return client.get_project_by_id(project_id)


# ----------------
# Project Users
# ----------------

def project_user_create(cmd, client, base_url, project_id, user_name, user_role, tags=None):
    user_definition = UserDefinition(
        email=user_name, role=user_role, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=user_definition,
                               create_func=client.create_project_user,
                               get_func=client.get_project_user_by_id,
                               project_id=project_id)


def project_user_delete(cmd, client, base_url, project_id, user_id):
    return _delete_with_status(cmd, client, base_url, user_id, client.delete_project_user, project_id)


def project_user_list(cmd, client, base_url, project_id):
    client._client.config.base_url = base_url
    return client.get_project_users(project_id)


def project_user_get(cmd, client, base_url, project_id, user_id):
    client._client.config.base_url = base_url
    return client.get_project_user_by_id(user_id, project_id)


# ----------------
# Project Types
# ----------------

def project_type_create(cmd, client, base_url, project_type_id):
    client._client.config.base_url = base_url
    project_type = ProjectType(id=project_type_id)
    return client.create_project_type(project_type)


def project_type_delete(cmd, client, base_url, project_type_id):
    client._client.config.base_url = base_url
    return client.delete_project_type(project_type_id)


def project_type_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_project_types()


def project_type_get(cmd, client, base_url, project_type_id):
    client._client.config.base_url = base_url
    return client.get_project_type_by_id(project_type_id)


# ----------------
# Providers
# ----------------

def provider_create(cmd, client, base_url, provider_id):
    provider = Provider(provider_id)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=provider,
                               create_func=client.create_provider,
                               get_func=client.get_provider_by_id)


def provider_delete(cmd, client, base_url, provider_id):
    return _delete_with_status(cmd, client, base_url, provider_id, client.delete_provider)


def provider_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_providers()


def provider_get(cmd, client, base_url, provider_id):
    client._client.config.base_url = base_url
    return client.get_provider_by_id(provider_id)


# ----------------
# Status
# ----------------

def status_get(cmd, client, base_url, tracking_id, project_id=None):
    client._client.config.base_url = base_url
    return client.get_project_status(project_id, tracking_id) if project_id else client.get_status(tracking_id)


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

        if result.code == 302:
            hook.add(message='{}: {}'.format(
                result.state, result.state_message or 'Creating new {}'.format(type_name)))

            item_id = urlparse(result.location).path.split('/')[-1]

            result = get_func(
                item_id, project_id) if project_id else get_func(item_id)

        if result.code == 202:
            for i in range(STATUS_POLLING_SLEEP_INTERVAL):
                hook.add(message='{}: {}'.format(
                    result.state, result.state_message or 'Creating new {}'.format(type_name)))
                sleep(1)

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
            for i in range(STATUS_POLLING_SLEEP_INTERVAL):
                hook.add(message='{}: {}'.format(
                    result.state, result.state_message or 'Deleting {}'.format(type_name)))
                sleep(1)

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
