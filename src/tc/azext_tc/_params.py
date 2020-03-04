# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type)
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

    # Global

    with self.argument_context('tc') as c:
        c.argument('name', options_list=['--name', '-n'],
                   help='Name of app.')
        c.argument('location', get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)

    # ignore global az arg --subscription for everything except `tc create`
    for scope in ['tc status', 'tc user', 'tc project', 'tc project-type', 'tc provider', 'tc tag']:
        with self.argument_context(scope, arg_group='Global') as c:
            c.ignore('_subscription')
            c.argument('base_url', tc_url_type)

    for scope in ['tc tag', 'tc project tag']:
        with self.argument_context(scope) as c:
            c.argument('tag_name', options_list=['--name', '-n'])
            c.argument('tag_value', options_list='--value')

    # TeamCloud

    with self.argument_context('tc create') as c:
        c.argument('config_yaml', options_list=['--config-yaml', '-c'],
                   type=str, help='TeamCloud configuration yaml file.')

    with self.argument_context('tc status') as c:
        c.argument('project', project_name_or_id_type)
        c.argument('tracking_id', options_list=['--tracking-id', '-t'],
                   type=str, help='Operation tracking id.',
                   validator=tracking_id_validator)

    # TeamCloud Users

    with self.argument_context('tc user create') as c:
        c.argument('user_name', user_name_type)
        c.argument('user_role', get_enum_type(['Admin', 'Creator'], default='Creator'),
                   options_list=['--role', '-r'], help='User role.')
        c.argument('tags', tags_type)

    for scope in ['tc user show', 'tc user delete']:
        with self.argument_context(scope) as c:
            c.argument('user', user_name_or_id_type)

    # Projects

    with self.argument_context('tc project create') as c:
        c.argument('name', options_list=['--name', '-n'],
                   type=str, help='Project name.',
                   validator=project_name_validator)
        c.argument('project_type', options_list=['--project-type', '-t'],
                   type=str, help='Project type id.',
                   validator=project_type_id_validator)
        c.argument('tags', tags_type)

    for scope in ['tc project show', 'tc project delete']:
        with self.argument_context(scope) as c:
            c.argument('project', options_list=['--name', '-n'],
                       type=str, help='Project name or id (uuid).',
                       validator=project_name_or_id_validator)

    with self.argument_context('tc project tag') as c:
        c.argument('project', project_name_or_id_type)

    # Project Users

    with self.argument_context('tc project user') as c:
        c.argument('project', project_name_or_id_type)

    with self.argument_context('tc project user create') as c:
        c.argument('user_name', user_name_type)
        c.argument('user_role', get_enum_type(['Owner', 'Member'], default='Member'),
                   options_list=['--role', '-r'], help='User role.')
        c.argument('tags', tags_type)

    for scope in ['tc project user show', 'tc project user delete']:
        with self.argument_context(scope) as c:
            c.argument('user', user_name_or_id_type)

    # Project Types

    # id: str VAL: project type id
    # default: bool
    # region: str (location) VAL: azure location
    # subscriptions: [str] >= 3 VAL: guid & maybe sub val
    # subscription_capacity: int
    # resource_group_name_prefix: str VAL:
    # providers: [ProviderReference] (id: str, properties: {str}) VAL: id is valid provider id
    # tags: {str}
    # properties: {str}

    with self.argument_context('tc project-type create') as c:
        c.argument('project_type', options_list=['--name', '-n'],
                   type=str, help='Project type id.',
                   validator=project_type_id_validator)
        c.argument('tags', tags_type)

    for scope in ['tc project-type show', 'tc project-type delete']:
        with self.argument_context(scope) as c:
            c.argument('project_type_id', options_list=['--name', '-n'],
                       type=str, help='Project type id.',
                       validator=project_type_id_validator)

    # Providers

    # id: str VAL: provider id
    # url: str VAL: url
    # auth_code: str
    # principal_id: str VAL: uuid
    # optional: bool
    # dependencies: ProviderDependenciesModel(create: [str], init: [str]) VAL: create & init are valid provider ids
    # events: [str] VAL: valid provider ids
    # properties: {str}

    with self.argument_context('tc provider create') as c:
        c.argument('provider', options_list=['--name', '-n'],
                   type=str, help='Provider id.',
                   validator=provider_id_validator)

    for scope in ['tc provider show', 'tc provider delete']:
        with self.argument_context(scope) as c:
            c.argument('provider', options_list=['--name', '-n'],
                       type=str, help='Provider id.',
                       validator=provider_id_validator)
