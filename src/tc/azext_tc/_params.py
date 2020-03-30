# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long, too-many-statements

from knack.arguments import CLIArgumentType
from azure.cli.core.commands.parameters import (
    tags_type,
    get_enum_type,
    get_location_type,
    resource_group_name_type)

from ._validators import (
    project_name_validator, project_name_or_id_validator, user_name_validator, user_name_or_id_validator,
    tracking_id_validator, project_type_id_validator, project_type_id_validator_name, provider_id_validator,
    subscriptions_list_validator, provider_event_list_validator, url_validator, base_url_validator, auth_code_validator)

from ._completers import (
    get_project_completion_list)

from ._actions import CreateProviderReference


def load_arguments(self, _):

    tc_url_type = CLIArgumentType(
        options_list=['--base-url', '-u'],
        help='Base url of the TeamCloud instance. Use `az configure --defaults tc-base-url=<url>` to configure a default.',
        configured_default='tc-base-url',
        validator=base_url_validator)

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
        validator=project_name_or_id_validator,
        completer=get_project_completion_list)

    # Global

    with self.argument_context('tc') as c:
        c.argument('name', options_list=['--name', '-n'],
                   help='Name of app.')
        c.argument('location', get_location_type(self.cli_ctx))
        c.argument('tags', tags_type)

    # ignore global az arg --subscription and requre base_url for everything except `tc create`
    for scope in ['tc status', 'tc upgrade', 'tc user', 'tc project', 'tc project-type', 'tc provider', 'tc tag']:
        with self.argument_context(scope, arg_group='TeamCloud Global') as c:
            c.ignore('_subscription')
            c.argument('base_url', tc_url_type)

    for scope in ['tc tag create', 'tc project tag create']:
        with self.argument_context(scope) as c:
            c.argument('tag_key', options_list=['--key', '-k'])

    for scope in ['tc tag show', 'tc tag delete', 'tc project tag show', 'tc project tag delete']:
        with self.argument_context(scope) as c:
            c.argument('tag_value', options_list=['--value', '-v'])

    # TeamCloud

    with self.argument_context('tc create') as c:
        c.argument('resource_group_name', arg_type=resource_group_name_type, default='TeamCloud')
        c.argument('principal_name', help='Service principal name, or object id.')
        c.argument('principal_password', help="Service principal password, aka 'client secret'.")
        c.argument('skip_deploy', action='store_true', help="Only create Azure resources, skip deploying the TeamCloud API and Orchestrator.")

    with self.argument_context('tc upgrade') as c:
        c.argument('version', options_list=['--version', '-v'],
                   type=str, help='TeamCloud release version.')
        c.argument('resource_group_name', arg_type=resource_group_name_type, default='TeamCloud')

    with self.argument_context('tc status') as c:
        c.argument('project', project_name_or_id_type, completer=get_project_completion_list)
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
                       validator=project_name_or_id_validator,
                       completer=get_project_completion_list)

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

    with self.argument_context('tc project-type create') as c:
        c.argument('project_type', options_list=['--name', '-n'],
                   type=str, help='Project type id.',
                   validator=project_type_id_validator_name)
        c.argument('location', get_location_type(self.cli_ctx),
                   help='Project type region.')
        c.argument('subscriptions', nargs='+',
                   help='Space-seperated subscription ids (3+).',
                   validator=subscriptions_list_validator)
        c.argument('subscription_capacity', type=int, default=10,
                   help='Maximum number of projects per subscription.')
        c.argument('default', action='store_true',
                   help='Set as the default project type.')
        c.argument('resource_group_name_prefix', type=str,
                   help='Prepended to all project resource group names.')
        c.argument('provider', nargs='+', action=CreateProviderReference,
                   help='Project type provider: provider_id [key=value ...]. Use depends_on key to define dependencies. Use multiple --provider arguemnts to specify multiple providers.')
        c.argument('tags', tags_type)
        c.argument('properties', tags_type,
                   help="Space-separated properties: key[=value][key[=value] ...]. Use '' to clear existing properties.")
        c.ignore('providers')

    for scope in ['tc project-type show', 'tc project-type delete']:
        with self.argument_context(scope) as c:
            c.argument('project_type', options_list=['--name', '-n'],
                       type=str, help='Project type id.',
                       validator=project_type_id_validator_name)

    # Providers

    with self.argument_context('tc provider create') as c:
        c.argument('provider', options_list=['--name', '-n'],
                   type=str, help='Provider id.',
                   validator=provider_id_validator)
        c.argument('url', type=str, help='Provider url.',
                   validator=url_validator)
        c.argument('auth_code', type=str, help='Provider auth code.',
                   validator=auth_code_validator)

    for scope in ['tc provider create', 'tc provider deploy']:
        with self.argument_context(scope) as c:
            c.argument('events', nargs='+',
                       help='Space-seperated provider ids.',
                       validator=provider_event_list_validator)
            c.argument('properties', tags_type,
                       help="Space-separated properties: key[=value][key[=value] ...]. Use '' to clear existing properties.")

    for scope in ['tc provider show', 'tc provider delete']:
        with self.argument_context(scope) as c:
            c.argument('provider', options_list=['--name', '-n'],
                       type=str, help='Provider id.',
                       validator=provider_id_validator)

    with self.argument_context('tc provider deploy') as c:
        c.argument('provider', get_enum_type(['azure.appinsights', 'azure.devops', 'azure.devtestlabs']),
                   options_list=['--name', '-n'], help='Provider id.')
        c.argument('version', options_list=['--version', '-v'],
                   type=str, help='Provider release version.')
        c.argument('resource_group_name',
                   arg_type=resource_group_name_type, default='TeamCloud-Providers',
                   help='Name of resource group.')
        c.argument('teamcloud_resource_group_name', options_list=['--teamcloud-resource-group'],
                   arg_type=resource_group_name_type, default='TeamCloud',
                   help='Name of TeamCloud resource group.')
