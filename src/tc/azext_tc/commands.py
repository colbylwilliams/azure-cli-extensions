# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_tc._client_factory import cf_tc
from ._transformers import (
    transform_output,
    transform_user_table_output,
    transform_project_table_output,
    transform_project_type_table_output,
    transform_provider_table_output)


def load_command_table(self, _):

    tc_sdk = CliCommandType(
        operations_tmpl='azext_tc.vendored_sdks.operations#TeamCloudClient.{}',
        client_factory=cf_tc)

    # ----------------
    # TeamCloud Users
    # ----------------

    with self.command_group('tc user', tc_sdk, client_factory=cf_tc) as g:
        g.custom_command('create', 'teamcloud_user_create',
                         transform=transform_output)
        g.custom_command('delete', 'teamcloud_user_delete',
                         transform=transform_output)
        g.custom_command('list', 'teamcloud_user_list',
                         transform=transform_output, table_transformer=transform_user_table_output)
        g.custom_show_command('show', 'teamcloud_user_get',
                              transform=transform_output)

    # ----------------
    # Projects
    # ----------------

    with self.command_group('tc project', tc_sdk, client_factory=cf_tc) as g:
        g.custom_command('create', 'project_create',
                         transform=transform_output)
        g.custom_command('delete', 'project_delete',
                         transform=transform_output)
        g.custom_command('list', 'project_list',
                         transform=transform_output, table_transformer=transform_project_table_output)
        g.custom_show_command('show', 'project_get',
                              transform=transform_output)

    # ----------------
    # Project Users
    # ----------------

    with self.command_group('tc project user', tc_sdk, client_factory=cf_tc) as g:
        g.custom_command('create', 'project_user_create',
                         transform=transform_output)
        g.custom_command('delete', 'project_user_delete',
                         transform=transform_output)
        g.custom_command('list', 'project_user_list',
                         transform=transform_output, table_transformer=transform_user_table_output)
        g.custom_show_command('show', 'project_user_get',
                              transform=transform_output)

    # ----------------
    # Project Types
    # ----------------

    with self.command_group('tc project-type', tc_sdk, client_factory=cf_tc) as g:
        g.custom_command('create', 'project_type_create',
                         transform=transform_output)
        g.custom_command('delete', 'project_type_delete',
                         transform=transform_output)
        g.custom_command('list', 'project_type_list',
                         transform=transform_output, table_transformer=transform_project_type_table_output)
        g.custom_show_command('show', 'project_type_get',
                              transform=transform_output)

    # ----------------
    # Providers
    # ----------------

    with self.command_group('tc provider', tc_sdk, client_factory=cf_tc) as g:
        g.custom_command('create', 'provider_create',
                         transform=transform_output)
        g.custom_command('delete', 'provider_delete',
                         transform=transform_output)
        g.custom_command('list', 'provider_list',
                         transform=transform_output, table_transformer=transform_provider_table_output)
        g.custom_show_command('show', 'provider_get',
                              transform=transform_output)

    # ----------------
    # Status
    # ----------------

    with self.command_group('tc', tc_sdk, client_factory=cf_tc) as g:
        g.custom_command('status', 'status_get',
                         transform=transform_output)

    with self.command_group('tc', is_preview=True):
        pass
