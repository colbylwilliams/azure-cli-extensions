# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

# Example of a storage account name or ID validator.
# See: https://github.com/Azure/azure-cli/blob/dev/doc/authoring_command_modules/authoring_commands.md#supporting-name-or-id-parameters
from uuid import UUID
from azure.cli.core.commands.client_factory import get_subscription_id
from msrestazure.tools import is_valid_resource_id, resource_id
from knack.log import get_logger

logger = get_logger(__name__)


def example_name_or_id_validator(cmd, namespace):
    if namespace.storage_account:
        if not is_valid_resource_id(namespace.RESOURCE):
            namespace.storage_account = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.Storage',
                type='storageAccounts',
                name=namespace.storage_account
            )

# def project_name_or_id_validator(cmd, namespace):
#     if namespace.project_name is not None:
#         if not is_valid_project_name(namespace.project_name) and not is_valid_uuid()


def is_valid_project_name(name):
    return name is not None and len(name) > 4


def is_valid_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    print(str(uuid_obj))
    return str(uuid_obj) == uuid_to_test
