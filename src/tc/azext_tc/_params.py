# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type)


def load_arguments(self, _):

    tc_url_type = CLIArgumentType(
        options_list=['--url', '-u'],
        help='Base url of the TeamCloud instance, you can configure the default url using `az configure -d tc-url=<url>`.',
        configured_default='tc-url')

    user_id_type = CLIArgumentType(
        options_list=['--name', '-n'],
        help='The ID or email address of the User.')

    project_id_type = CLIArgumentType(
        options_list=['--project', '-p'],
        help='The ID of the Project.')

    # ----------------
    # ALL
    # ----------------

    with self.argument_context('tc') as c:
        c.argument("base_url", arg_type=tc_url_type)
        c.ignore('_subscription')

    # ----------------
    # TeamCloud Users
    # ----------------

    with self.argument_context('tc user create') as c:
        c.argument('user_name', options_list=['--name', '-n'],
                   type=str, help='The email address or pricipal id of the User.')

        c.argument('user_role', options_list=['--role', '-r'],
                   arg_type=get_enum_type(['Admin', 'Creator']),
                   help='The email address or pricipal id of the User.')

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc user show', 'tc user delete']:
        with self.argument_context(scope) as c:
            c.argument('user_id', arg_type=user_id_type)

    # ----------------
    # Projects
    # ----------------

    with self.argument_context('tc project create') as c:
        c.argument('project_name', options_list=['--name', '-n'],
                   type=str, help='The name of the Project.')

        c.argument('project_type', options_list=['--project-type', '-t'],
                   type=str, help='The id of the Project Type to use for the Project.')

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc project show', 'tc project delete']:
        with self.argument_context(scope) as c:
            c.argument('project_id', options_list=['--name', '-n'],
                       type=str, help='The name or id of the Project.')

    # ----------------
    # Project Users
    # ----------------

    with self.argument_context('tc project user') as c:
        c.argument('project_id', arg_type=project_id_type)

    with self.argument_context('tc project user create') as c:
        c.argument('user_name', options_list=['--name', '-n'],
                   type=str, help='The email address or pricipal id of the User.')

        c.argument('user_role', options_list=['--role', '-r'],
                   arg_type=get_enum_type(['Owner', 'Member']),
                   help='The email address or pricipal id of the User.')

        c.argument('tags', arg_type=tags_type)

    for scope in ['tc project user show', 'tc project user delete']:
        with self.argument_context(scope) as c:
            c.argument('user_id', arg_type=user_id_type)

    # ----------------
    # Project Types
    # ----------------

    with self.argument_context('tc project-type create') as c:
        c.argument('project_type_id', options_list=['--id', '-i'],
                   type=str, help='The ID of the Project Type.')

    for scope in ['tc project-type show', 'tc project-type delete']:
        with self.argument_context(scope) as c:
            c.argument('project_type_id', options_list=['--id', '-i'],
                       type=str, help='The ID of the Project Type.')

    # ----------------
    # Providers
    # ----------------

    with self.argument_context('tc provider create') as c:
        c.argument('provider_id', options_list=['--id', '-i'],
                   type=str, help='The ID of the Provider.')

    for scope in ['tc provider show', 'tc provider delete']:
        with self.argument_context(scope) as c:
            c.argument('provider_id', options_list=['--id', '-i'],
                       type=str, help='The ID of the Provider.')

    # ----------------
    # Status
    # ----------------

    with self.argument_context('tc status') as c:
        c.argument('tracking_id', options_list=['--tracking-id', '-t'],
                   type=str, help='The tracking ID of the operation.')

        c.argument('project_id', arg_type=project_id_type)

    # with self.argument_context('tc') as c:
    #     c.argument('tags', tags_type)
    #     c.argument('location', validator=get_default_location_from_resource_group)
    #     c.argument('tc_name', tc_name_type, options_list=['--name', '-n'])

    # with self.argument_context('tc list') as c:
    #     c.argument('tc_name', tc_name_type, id_part=None)
