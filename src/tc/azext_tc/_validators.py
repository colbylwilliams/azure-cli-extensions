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

logger = get_logger(__name__)

# pylint: disable=unused-argument, protected-access


def project_name_validator(cmd, namespace):
    if namespace.name is not None:
        if _is_valid_uuid(namespace.name):
            return
        if not _is_valid_project_name(namespace.name):
            raise CLIError(
                '--project should be a valid uuid or a project name string with length [4,31]')


def project_name_or_id_validator(cmd, namespace):
    if namespace.project:
        if _is_valid_uuid(namespace.project):
            return
        if not _is_valid_project_name(namespace.project):
            raise CLIError(
                '--project should be a valid uuid or a project name string with length [4,31]')

        from ._client_factory import teamcloud_client_factory

        client = teamcloud_client_factory(cmd.cli_ctx)
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
        if not _has_basic_email_format(namespace.user_name):
            raise CLIError(
                '--name should be a user name in eamil format')


def user_name_or_id_validator(cmd, namespace):
    if namespace.user:
        if _is_valid_uuid(namespace.user):
            return
        if not _has_basic_email_format(namespace.user):
            raise CLIError(
                '--user should be a valid uuid or a user name in eamil format')


def project_type_id_validator(cmd, namespace):
    if namespace.project_type:
        if not _is_valid_project_type_id(namespace.project_type):
            raise CLIError(
                '--project-type should start with a lowercase and contain only lowercase, numbers, and periods [.] with length [4,254]')


def project_type_id_validator_name(cmd, namespace):
    if namespace.project_type:
        if not _is_valid_project_type_id(namespace.project_type):
            raise CLIError(
                '--name should start with a lowercase and contain only lowercase, numbers, and periods [.] with length [4,254]')


def provider_id_validator(cmd, namespace):
    if namespace.provider:
        if not _is_valid_provider_id(namespace.provider):
            raise CLIError(
                '--name should start with a lowercase and contain only lowercase, numbers, and periods [.] with length [4,254]')


def subscriptions_list_validator(cmd, namespace):
    if namespace.subscriptions:
        if len(namespace.subscriptions) < 3 or not all(_is_valid_uuid(x) for x in namespace.subscriptions):
            raise CLIError(
                '--subscriptions should be a space-separated list of at least 3 valid uuids')


def provider_event_list_validator(cmd, namespace):
    if namespace.events:
        if not all(_is_valid_provider_id(x) for x in namespace.events):
            raise CLIError(
                '--events should be a space-separated list of valid provider ids, provider ids should start with a lowercase and contain only lowercase, numbers, and periods [.] with length [4,254]')


def provider_create_dependencies_validator(cmd, namespace):
    if namespace.create_dependencies:
        if not all(_is_valid_provider_id(x) for x in namespace.create_dependencies):
            raise CLIError(
                '--create-dependencies should be a space-separated list of valid provider ids, provider ids should start with a lowercase and contain only lowercase, numbers, and periods [.] with length [4,254]')


def provider_init_dependencies_validator(cmd, namespace):
    if namespace.init_dependencies:
        if not all(_is_valid_provider_id(x) for x in namespace.init_dependencies):
            raise CLIError(
                '--create-dependencies should be a space-separated list of valid provider ids, provider ids should start with a lowercase and contain only lowercase, numbers, and periods [.] with length [4,254]')


def tc_resource_name_validator(cmd, namespace):
    if namespace.name:
        if match(r'^[^\\/\?#]{2,254}$', namespace.name) is None:
            raise CLIError(
                r"--name should have length [2,254] and not include characters [ '\\', '/', '?', '#' ]")


def tracking_id_validator(cmd, namespace):
    if namespace.tracking_id:
        if not _is_valid_uuid(namespace.tracking_id):
            raise CLIError(
                '--tracking-id should be a valid uuid')


def url_validator(cmd, namespace):
    if namespace.url:
        if not _is_valid_url(namespace.url):
            raise CLIError(
                '--url should be a valid url')


def base_url_validator(cmd, namespace):
    if namespace.base_url:
        if not _is_valid_url(namespace.url):
            raise CLIError(
                '--base-url should be a valid url')


def auth_code_validator(cmd, namespace):
    if namespace.auth_code:
        if not _is_valid_functions_auth_code(namespace.auth_code):
            raise CLIError(
                '--auth-code should contain only base-64 digits [A-Za-z0-9/] (excluding the plus sign (+)), ending in = or ==')


def _is_valid_project_name(name):
    return name is not None and 4 < len(name) < 31


def _is_valid_project_type_id(project_type_id):
    return 4 <= len(project_type_id) <= 255 and match(r'^(?:[a-z][a-z0-9]+(?:\.[a-z0-9]+)+)$', project_type_id) is not None


def _is_valid_provider_id(provider_id):
    return 4 <= len(provider_id) <= 255 and match(r'^(?:[a-z][a-z0-9]+(?:\.[a-z0-9]+)+)$', provider_id) is not None


def _is_valid_resource_id(resource_id):
    return match(r'^[^\\/\?#]{2,255}$', resource_id) is not None


def _has_basic_email_format(email):
    """Basic email check to ensure it has exactly one @ sign,
    and at least one . in the part after the @ sign
    """
    return match(r'^[^@]+@[^@]+\.[^@]+$', email) is not None


def _is_valid_url(url):
    return match(r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$', url) is not None


def _is_valid_functions_auth_code(auth_code):
    """Validates a string only contains base-64 digits,
    minus the plus sign (+) [A-Za-z0-9/], ends in = or ==
    https://github.com/Azure/azure-functions-host/blob/dev/src/WebJobs.Script.WebHost/Security/KeyManagement/SecretManager.cs#L592-L603
    """
    return match(r'^([A-Za-z0-9/]{4})*([A-Za-z0-9/]{3}=|[A-Za-z0-9/]{2}==)?$', auth_code) is not None


def _is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test
