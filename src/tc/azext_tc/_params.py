# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type)
from ._validators import (
    project_name_validator,
    project_name_or_id_validator,
    user_name_validator,
    user_name_or_id_validator,
    tracking_id_validator,
    project_type_id_validator,
    provider_id_validator)


def load_arguments(self, _):

    tc_url_type = CLIArgumentType(
        options_list=['--url', '-u'],
        help='Base url of the TeamCloud instance. Use `az configure --defaults tc-url=<url>` to configure a default.',
        configured_default='tc-url')

    user_name_type = CLIArgumentType(
        options_list=['--name', '-n'],
        help='User email or principal id.',
        validator=user_name_validator)

    user_name_or_id_type = CLIArgumentType(
        options_list=['--name', '-n'],
        help='User id, email, or principal id.',
        validator=user_name_or_id_validator)

    project_name_or_id_type = CLIArgumentType(
        options_list=['--project', '-p'],
        help='Project name or id (uuid).',
        validator=project_name_or_id_validator)

    # ----------------
    # TeamCloud
    # ----------------

    with self.argument_context('tc') as c:
        c.argument('base_url', arg_type=tc_url_type)
        # c.argument('raw_response',
        #            options_list=['--raw'], help='Return raw server response opposed result object. ', action='store_true')
        c.ignore('_subscription')

    with self.argument_context('tc create') as c:
        c.argument('config_yaml', options_list=['--config-yaml', '-c'],
                   type=str, help='TeamCloud configuration yaml file.')

    with self.argument_context('tc status') as c:
        c.argument('tracking_id', options_list=['--tracking-id', '-t'],
                   type=str, help='Operation tracking id.',
                   validator=tracking_id_validator)

        c.argument('project', arg_type=project_name_or_id_type)

    # ----------------
    # TeamCloud Users
    # ----------------

    with self.argument_context('tc user create') as c:
        c.argument('user_name', arg_type=user_name_type)

        c.argument('user_role', options_list=['--role', '-r'],
                   arg_type=get_enum_type(
                       ['Admin', 'Creator'], default='Creator'),
                   help='User role.')

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc user show', 'tc user delete']:
        with self.argument_context(scope) as c:
            c.argument('user', arg_type=user_name_or_id_type)

    # ----------------
    # Projects
    # ----------------

    with self.argument_context('tc project create') as c:
        c.argument('name', options_list=['--name', '-n'],
                   type=str, help='Project name.',
                   validator=project_name_validator)

        c.argument('project_type', options_list=['--project-type', '-t'],
                   type=str, help='Project type id.',
                   validator=project_type_id_validator)

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc project show', 'tc project delete']:
        with self.argument_context(scope) as c:
            c.argument('project', options_list=['--name', '-n'],
                       type=str, help='Project name or id (uuid).',
                       validator=project_name_or_id_validator)

    # ----------------
    # Project Users
    # ----------------

    with self.argument_context('tc project user') as c:
        c.argument('project', arg_type=project_name_or_id_type)

    with self.argument_context('tc project user create') as c:
        c.argument('user_name', arg_type=user_name_type)

        c.argument('user_role', options_list=['--role', '-r'],
                   arg_type=get_enum_type(
                       ['Owner', 'Member'], default='Member'),
                   help='User role.')

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc project user show', 'tc project user delete']:
        with self.argument_context(scope) as c:
            c.argument('user', arg_type=user_name_or_id_type)

    # ----------------
    # Project Types
    # ----------------

    with self.argument_context('tc project-type create') as c:
        c.argument('project_type', options_list=['--name', '-n'],
                   type=str, help='Project type id.',
                   validator=project_type_id_validator)

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc project-type show', 'tc project-type delete']:
        with self.argument_context(scope) as c:
            c.argument('project_type_id', options_list=['--name', '-n'],
                       type=str, help='Project type id.',
                       validator=project_type_id_validator)

    # ----------------
    # Providers
    # ----------------

    with self.argument_context('tc provider create') as c:
        c.argument('provider', options_list=['--name', '-n'],
                   type=str, help='Provider id.',
                   validator=provider_id_validator)

    for scope in ['tc provider show', 'tc provider delete']:
        with self.argument_context(scope) as c:
            c.argument('provider', options_list=['--name', '-n'],
                       type=str, help='Provider id.',
                       validator=provider_id_validator)

    # with self.argument_context('tc') as c:
    #     c.argument('tags', tags_type)
    #     c.argument('location', validator=get_default_location_from_resource_group)
    #     c.argument('tc_name', tc_name_type, options_list=['--name', '-n'])

    # with self.argument_context('tc list') as c:
    #     c.argument('tc_name', tc_name_type, id_part=None)
