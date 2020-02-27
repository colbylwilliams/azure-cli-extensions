# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

# Example of a storage account name or ID validator.
# See: https://github.com/Azure/azure-cli/blob/dev/doc/authoring_command_modules/authoring_commands.md#supporting-name-or-id-parameters
from re import match
from uuid import UUID
from azure.cli.core.util import CLIError
from knack.log import get_logger
from azext_tc.vendored_sdks.teamcloud.models import ErrorResult
from ._client_factory import cf_tc

logger = get_logger(__name__)

# pylint: disable=unused-argument, protected-access


def project_name_validator(cmd, namespace):
    # logger.warning('validating')
    if namespace.name is not None:
        if is_valid_uuid(namespace.name):
            return
        if not is_valid_project_name(namespace.name):
            raise CLIError(
                '--project should be a valid uuid or a project name string with length [4,31]')


def project_name_or_id_validator(cmd, namespace):
    if namespace.project:
        if is_valid_uuid(namespace.project):
            return
        if not is_valid_project_name(namespace.project):
            raise CLIError(
                '--project should be a valid uuid or a project name string with length [4,31]')

        client = cf_tc(cmd.cli_ctx)
        client._client.config.base_url = namespace.base_url
        result = client.get_project_by_name_or_id(namespace.project)

        if isinstance(result, ErrorResult):
            raise CLIError(
                '--project no project found matching provided project name')
        try:
            namespace.project = result.data.id
        except AttributeError:
            pass


def user_name_validator(cmd, namespace):
    if namespace.user_name:
        if not has_basic_email_format(namespace.user_name):
            raise CLIError(
                '--name should be a user name in eamil format')


def user_name_or_id_validator(cmd, namespace):
    if namespace.user:
        if is_valid_uuid(namespace.user):
            return
        if not has_basic_email_format(namespace.user):
            raise CLIError(
                '--user should be a valid uuid or a user name in eamil format')


def project_type_id_validator(cmd, namespace):
    if namespace.project_type:
        if match(r'^[^\\/\?#]{2,254}$', namespace.project_type) is None:
            raise CLIError(
                r"--project-type should have length [2,254] and not include characters [ '\\', '/', '?', '#' ]")


def provider_id_validator(cmd, namespace):
    if match(r'^(?:[a-z]+(?:\.[a-z]+)+)$', namespace.name) is None:
        raise CLIError(
            '--name should only contain lowercase letters and periods [.] with length [4,31]')


def tc_resource_name_validator(cmd, namespace):
    if namespace.name:
        if match(r'^[^\\/\?#]{2,254}$', namespace.name) is None:
            raise CLIError(
                r"--name should have length [2,254] and not include characters [ '\\', '/', '?', '#' ]")


def tracking_id_validator(cmd, namespace):
    if namespace.tracking_id:
        if not is_valid_uuid(namespace.tracking_id):
            raise CLIError(
                '--tracking-id should be a valid uuid')


def is_valid_resource_id(resource_id):
    return match(r'^[^\\/\?#]{2,255}$', resource_id) is not None


def has_basic_email_format(email):
    """Basic email check to ensure it has exactly one @ sign,
    and at least one . in the part after the @ sign
    """
    return match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


def is_valid_project_name(name):
    return name is not None and len(name) > 4 and len(name) < 31


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test
