# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from time import sleep
from urllib.parse import urlparse
from knack.util import CLIError
from knack.log import get_logger
from azure.cli.core.commands import LongRunningOperation
from azure.cli.core.profiles import ResourceType, get_sdk
from azure.cli.core.util import sdk_no_wait

# TODO: REMOVE THIS
# import urllib3  # pylint: disable=wrong-import-order
# urllib3.disable_warnings()

logger = get_logger(__name__)

STATUS_POLLING_SLEEP_INTERVAL = 2

# pylint: disable=unused-argument, protected-access, line-too-long, too-many-locals


# TeamCloud


def teamcloud_create(cmd, client, name, location, resource_group_name=None, principal_name=None, principal_password=None, tags=None, skip_deploy=False):
    # from azure.cli.core.util import random_string
    from azure.cli.core._profile import Profile

    cli_ctx = cmd.cli_ctx

    location = location.lower()
    rg_name = resource_group_name or 'TeamCloud'

    logger.warning('Getting resource group...')
    rg, subscription_id = _get_resource_group_by_name(cli_ctx, rg_name)
    if rg is None:
        logger.warning('Creating resource group...')
        _create_resource_group_name(cli_ctx, rg_name, location)

    name_short = ''
    for n in name.lower():
        if n.isalpha() or n.isdigit():
            name_short += n

    if len(name_short) > 14:
        name_short = name_short[:14]

    logger.warning('Creating app insights...')
    appinsights = _try_create_application_insights(cli_ctx, name_short + 'appinsights', rg_name, location)

    logger.warning('Creating deployment storage account...')
    dep_storage = _create_storage_account(cli_ctx, name_short + 'depstorage', rg_name, location, tags)

    logger.warning('Creating task hub storage account...')
    th_storage = _create_storage_account(cli_ctx, name_short + 'thtorage', rg_name, location, tags)

    logger.warning('Creating web jobs storage account...')
    wj_storage = _create_storage_account(cli_ctx, name_short + 'wjstorage', rg_name, location, tags)

    logger.warning('Creating cosmos db account. This will take several minutes to complete...')
    cosmosdb = _create_cosmosdb_account(cli_ctx, name_short + 'database', rg_name, location, tags)

    profile = Profile(cli_ctx=cli_ctx)

    if principal_name is None and principal_password is None:
        logger.warning('Creating aad app registration...')
        resource_manager_sp = _create_resource_manager_sp(cmd)
    else:
        _, _, tenant_id = profile.get_login_credentials(resource=cli_ctx.cloud.endpoints.active_directory_graph_resource_id)
        resource_manager_sp = {
            'appId': principal_name,
            'password': principal_password,
            'tenant': tenant_id
        }

    logger.warning('Creating app configuration service...')
    appconfig = _create_appconfig(cli_ctx, name + '-config', rg_name, location, tags)

    logger.warning('Adding resource info to app configuration service...')
    _set_appconfig_keys(cli_ctx, subscription_id, resource_manager_sp, appconfig, cosmosdb, dep_storage)

    logger.warning('Creating orchestrator function app...')
    orchestrator, orchestrator_host_key = _create_function_app(cli_ctx, name + '-orchestrator', rg_name, location,
                                                               wj_storage, th_storage, appconfig, appinsights, tags)

    logger.warning('Adding orchestrator info to app configuration service...')
    _set_appconfig_orchestrator_keys(cli_ctx, subscription_id, appconfig, orchestrator, orchestrator_host_key)

    logger.warning('Creating api app service...')
    api_app = _create_api_app(cli_ctx, name, rg_name, location, appconfig, appinsights, tags)

    logger.warning('Successfully deployed Azure resources for TeamCloud')

    if skip_deploy:
        logger.warning('IMPORTANT: --skip-deploy prevented source code for the TeamCloud instance deployment. To deploy the applicaitons use `az tc upgrade`.')

    else:
        logger.warning('Deploying orchestrator source code...')
        # _zip_deploy_app(cli_ctx, rg_name, name + '-orchestrator', 'https://github.com/microsoft/TeamCloud', 'TeamCloud.Orchestrator', version=None, app_instance=orchestrator)
        _zip_deploy_app(cli_ctx, rg_name, name + '-orchestrator', 'https://github.com/microsoft/TeamCloud',
                        'TeamCloud.Orchestrator', version='v0.1.1-alpha.1', app_instance=orchestrator)

        logger.warning('Deploying api app source code...')
        # _zip_deploy_app(cli_ctx, rg_name, name, 'https://github.com/microsoft/TeamCloud', 'TeamCloud.API', version=None, app_instance=api_app)
        _zip_deploy_app(cli_ctx, rg_name, name, 'https://github.com/microsoft/TeamCloud', 'TeamCloud.API', version='v0.1.1-alpha.1', app_instance=api_app)

        logger.warning('Successfully created TeamCloud instance.')
        base_url = 'https://{}'.format(api_app.default_host_name)

        logger.warning('Creating admin user...')
        me = profile.get_current_account_user()
        user = teamcloud_user_create(cmd, client, base_url, me, user_role='Admin')

    return 'TeamCloud instance successfully created at: {}. Use `az configure --defaults tc-base-url={}` to configure this as your default TeamCloud instance'.format(base_url, base_url)


def teamcloud_upgrade(cmd, client, base_url, resource_group_name=None, version=None):
    rg_name = resource_group_name or 'TeamCloud'

    logger.warning('Getting resource group...')
    rg, _ = _get_resource_group_by_name(cmd.cli_ctx, rg_name)
    if rg is None:
        raise CLIError("Resource Group 'TeamCLoud' must exist in current subscription.")

    from re import match

    name = ''
    m = match(r'^https?://(?P<name>[a-zA-Z0-9-]+)\.azurewebsites\.net[/a-zA-Z0-9.\:]*$', base_url)
    try:
        name = m.group('name') if m is not None else None
    except IndexError:
        pass

    if name is None or '':
        raise CLIError("Unable to get app name from base url.")

    # logger.warning(name)

    logger.warning('Deploying orchestrator source code (version: %s)...', version)
    _zip_deploy_app(cmd.cli_ctx, rg_name, name + '-orchestrator', 'https://github.com/microsoft/TeamCloud', 'TeamCloud.Orchestrator', version=version)

    logger.warning('Deploying api app source code (version: %s)...', version)
    _zip_deploy_app(cmd.cli_ctx, rg_name, name, 'https://github.com/microsoft/TeamCloud', 'TeamCloud.API', version=version)

    return name


def status_get(cmd, client, base_url, tracking_id, project=None):
    client._client.config.base_url = base_url
    return client.get_project_status(project, tracking_id) if project else client.get_status(tracking_id)


# TeamCloud Users

def teamcloud_user_create(cmd, client, base_url, user_name, user_role='Creator', tags=None):
    from azext_tc.vendored_sdks.teamcloud.models import UserDefinition
    user_definition = UserDefinition(
        email=user_name, role=user_role, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=user_definition,
                               create_func=client.create_team_cloud_user)


def teamcloud_user_delete(cmd, client, base_url, user):
    return _delete_with_status(cmd, client, base_url, user, client.delete_team_cloud_user)


def teamcloud_user_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_team_cloud_users()


def teamcloud_user_get(cmd, client, base_url, user):
    client._client.config.base_url = base_url
    return client.get_team_cloud_user_by_name_or_id(user)


# TeamCloud Tags

def teamcloud_tag_create(cmd, client, base_url, tag_key, tag_value):
    client._client.config.base_url = base_url
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload={tag_key, tag_value},
                               create_func=client.create_team_cloud_tag)


def teamcloud_tag_delete(cmd, client, base_url, tag_key):
    client._client.config.base_url = base_url
    return _delete_with_status(cmd, client, base_url, tag_key, client.delete_team_cloud_tag)

# TODO update


def teamcloud_tag_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_team_cloud_tags()


def teamcloud_tag_get(cmd, client, base_url, tag_key):
    client._client.config.base_url = base_url
    return client.get_team_cloud_tag_by_key(tag_key)


# Projects

def project_create(cmd, client, base_url, name, project_type=None, tags=None):
    from azext_tc.vendored_sdks.teamcloud.models import ProjectDefinition
    project_definition = ProjectDefinition(
        name=name, project_type=project_type, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=project_definition,
                               create_func=client.create_project)


def project_delete(cmd, client, base_url, project, no_wait=False):
    # _delete_with_status(cmd, client, base_url, project, client.delete_project)
    return sdk_no_wait(no_wait, _delete_with_status, cmd, client, base_url, project, client.delete_project)


def project_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_projects()


def project_get(cmd, client, base_url, project):
    client._client.config.base_url = base_url
    return client.get_project_by_name_or_id(project)


# Project Users

def project_user_create(cmd, client, base_url, project, user_name, user_role='Member', tags=None):
    from azext_tc.vendored_sdks.teamcloud.models import UserDefinition
    user_definition = UserDefinition(
        email=user_name, role=user_role, tags=tags)
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=user_definition,
                               create_func=client.create_project_user,
                               project_id=project)


def project_user_delete(cmd, client, base_url, project, user):
    return _delete_with_status(cmd, client, base_url, user, client.delete_project_user, project)


def project_user_list(cmd, client, base_url, project):
    client._client.config.base_url = base_url
    return client.get_project_users(project)


def project_user_get(cmd, client, base_url, project, user):
    client._client.config.base_url = base_url
    return client.get_project_user_by_name_or_id(user, project)


# Project Tags

def project_tag_create(cmd, client, base_url, project, tag_key, tag_value):
    client._client.config.base_url = base_url
    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload={tag_key, tag_value},
                               create_func=client.create_project_tag,
                               project_id=project)


def project_tag_delete(cmd, client, base_url, project, tag_key):
    client._client.config.base_url = base_url
    return _delete_with_status(cmd, client, base_url, tag_key, client.delete_project_tag, project)

# TODO update


def project_tag_list(cmd, client, base_url, project):
    client._client.config.base_url = base_url
    return client.get_project_tags(project)


def project_tag_get(cmd, client, base_url, project, tag_key):
    client._client.config.base_url = base_url
    return client.get_project_tag_by_key(project, tag_key)


# Project Types

def project_type_create(cmd, client, base_url, project_type, subscriptions, provider, providers, location=None, subscription_capacity=10, resource_group_name_prefix=None, tags=None, properties=None, default=False):
    from azext_tc.vendored_sdks.teamcloud.models import ProjectType
    client._client.config.base_url = base_url
    proj_type = ProjectType(
        id=project_type,
        default=default,
        region=location,
        subscriptions=subscriptions,
        subscription_capacity=subscription_capacity,
        resource_group_name_prefix=resource_group_name_prefix,
        providers=providers,
        tags=tags,
        properties=properties)
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


# Providers

def provider_create(cmd, client, base_url, provider, url, auth_code, events=None, properties=None):
    from azext_tc.vendored_sdks.teamcloud.models import Provider

    payload = Provider(
        id=provider,
        url=url,
        auth_code=auth_code,
        events=events,
        properties=properties,
    )

    return _create_with_status(cmd=cmd,
                               client=client,
                               base_url=base_url,
                               payload=payload,
                               create_func=client.create_provider)


def provider_delete(cmd, client, base_url, provider):
    return _delete_with_status(cmd, client, base_url, provider, client.delete_provider)


def provider_list(cmd, client, base_url):
    client._client.config.base_url = base_url
    return client.get_providers()


def provider_get(cmd, client, base_url, provider):
    client._client.config.base_url = base_url
    return client.get_provider_by_id(provider)


def provider_deploy(cmd, client, base_url, provider, version=None, resource_group_name=None, teamcloud_resource_group_name=None, events=None, properties=None):
    client._client.config.base_url = base_url
    from azure.cli.core.util import random_string
    cli_ctx = cmd.cli_ctx

    # TODO: Get TeamCloud location, tags ect.
    tags = None

    tc_rg_name = teamcloud_resource_group_name or 'TeamCloud'
    rg_name = resource_group_name or 'TeamCloud-Providers'

    logger.warning('Getting TeamCloud resource group...')
    teamcloud_rg, _ = _get_resource_group_by_name(cli_ctx, tc_rg_name)
    if teamcloud_rg is None:
        raise CLIError("Resource Group '{}' must exist in current subscription.".format(tc_rg_name))

    logger.warning('Getting TeamCloud-Providers resource group...')
    rg, _ = _get_resource_group_by_name(cli_ctx, rg_name)
    if rg is None:
        logger.warning('Creating TeamCloud-Providers group...')
        _create_resource_group_name(cli_ctx, rg_name, teamcloud_rg.location)

    name = random_string(length=14, force_lower=True)
    location = rg.location.lower()

    logger.warning('Creating task hub storage account...')
    th_storage = _create_storage_account(cli_ctx, name + 'thtorage', rg_name, location, tags)

    logger.warning('Creating web jobs storage account...')
    wj_storage = _create_storage_account(cli_ctx, name + 'wjstorage', rg_name, location, tags)

    zip_name = None
    if provider == 'azure.appinsights':
        zip_name = 'TeamCloud.Providers.Azure.AppInsights'
    if provider == 'azure.devops':
        zip_name = 'TeamCloud.Providers.Azure.DevOps'
    if provider == 'azure.devtestlabs':
        zip_name = 'TeamCloud.Providers.Azure.DevTestLabs'

    if zip_name is None:
        raise CLIError("--providers is invalid.  Must be one of 'azure.appinsights', 'azure.devops', 'azure.devtestlabs'")

    functionapp, host_key = _create_function_app(cli_ctx, name, rg_name, location, wj_storage, th_storage, tags=tags)

    url = 'https://{}'.format(functionapp.default_host_name)

    logger.warning('Deploying provider source code...')
    _zip_deploy_app(cli_ctx, rg_name, name, 'https://github.com/microsoft/TeamCloud-Providers', zip_name, version=version, app_instance=functionapp)

    return provider_create(cmd, client, base_url, provider, url, host_key, events, properties)


# Util

def _create_with_status(cmd, client, base_url, payload, create_func, project_id=None):
    from azext_tc.vendored_sdks.teamcloud.models import StatusResult
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


def _delete_with_status(cmd, client, base_url, item_id, delete_func, project_id=None, **kwargs):
    from azext_tc.vendored_sdks.teamcloud.models import StatusResult
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


def _get_resource_group_by_name(cli_ctx, resource_group_name):
    from azext_tc._client_factory import resource_client_factory
    try:
        resouce_client = resource_client_factory(cli_ctx).resource_groups
        return resouce_client.get(resource_group_name), resouce_client.config.subscription_id
    except Exception as ex:  # pylint: disable=broad-except
        error = getattr(ex, 'Azure Error', ex)
        if error != 'ResourceGroupNotFound':
            return None, resouce_client.config.subscription_id
        raise


def _create_resource_group_name(cli_ctx, resource_group_name, location, tags=None):
    from azext_tc._client_factory import resource_client_factory
    ResourceGroup = get_sdk(
        cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES, 'ResourceGroup', mod='models')
    resource_client = resource_client_factory(cli_ctx).resource_groups
    parameters = ResourceGroup(location=location, tags=tags)
    resource_client.create_or_update(resource_group_name, parameters)


def _create_storage_account(cli_ctx, name, resource_group_name, location, tags):
    from azext_tc._client_factory import storage_client_factory
    from azure.mgmt.storage.models import Sku, SkuName, StorageAccountCreateParameters
    params = StorageAccountCreateParameters(sku=Sku(name=SkuName.standard_ragrs),
                                            kind='StorageV2',
                                            location=location,
                                            tags=tags)

    storage_client = storage_client_factory(cli_ctx).storage_accounts
    LongRunningOperation(cli_ctx)(storage_client.create(resource_group_name, name, params))

    properties = storage_client.get_properties(resource_group_name, name)
    keys = storage_client.list_keys(resource_group_name, name)

    endpoint_suffix = cli_ctx.cloud.suffixes.storage_endpoint
    connection_string = 'DefaultEndpointsProtocol={};EndpointSuffix={};AccountName={};AccountKey={}'.format(
        "https",
        endpoint_suffix,
        name,
        keys.keys[0].value)  # pylint: disable=no-member

    return properties, keys, connection_string


def _create_cosmosdb_account(cli_ctx, name, resource_group_name, location, tags=None):
    from azext_tc._client_factory import cosmosdb_client_factory
    from azure.mgmt.cosmosdb.models import DatabaseAccountKind, Location, DatabaseAccountCreateUpdateParameters
    locations = []
    locations.append(Location(location_name=location, failover_priority=0, is_zone_redundant=False))
    params = DatabaseAccountCreateUpdateParameters(
        location=location,
        locations=locations,
        tags=tags,
        kind=DatabaseAccountKind.global_document_db.value)

    cosmos_client = cosmosdb_client_factory(cli_ctx).database_accounts

    async_docdb_create = cosmos_client.create_or_update(resource_group_name, name, params)
    docdb_account = async_docdb_create.result()
    docdb_account = cosmos_client.get(resource_group_name, name)  # Workaround

    connection_strings = cosmos_client.list_connection_strings(resource_group_name, name)

    return docdb_account, connection_strings.connection_strings[0].connection_string


def _create_appconfig(cli_ctx, name, resource_group_name, location, tags=None):
    from azext_tc._client_factory import appconfig_client_factory
    from azure.mgmt.appconfiguration.models import ConfigurationStore, Sku
    params = ConfigurationStore(location=location.lower(),
                                identity=None,
                                sku=Sku(name='Standard'),
                                tags=tags)

    appconfig_client = appconfig_client_factory(cli_ctx).configuration_stores

    LongRunningOperation(cli_ctx)(appconfig_client.create(resource_group_name, name, params))

    appconfig = appconfig_client.get(resource_group_name, name)
    keys = appconfig_client.list_keys(resource_group_name, name)

    key = next((k for k in keys if not k.read_only), None)

    return appconfig, keys, key.connection_string


def _set_appconfig_keys(cli_ctx, subscription_id, resource_manager_sp, appconfig, cosmosdb, dep_storage):
    from azure.cli.command_modules.appconfig._azconfig.azconfig_client import AzconfigClient
    from azure.cli.command_modules.appconfig._azconfig.models import KeyValue

    azconfig_client = AzconfigClient(appconfig[2])

    tenant_id = resource_manager_sp['tenant']

    set_kvs = []

    set_kvs.append(KeyValue(key='Azure:SubscriptionId', value=subscription_id))
    set_kvs.append(KeyValue(key='Azure:TenantId', value=tenant_id))

    # set_kvs.append(KeyValue(key='Azure:ActiveDirectory:ClientId', value=resource_manager_sp['appId']))
    # set_kvs.append(KeyValue(key='Azure:ActiveDirectory:Domain', value=''))
    # set_kvs.append(KeyValue(key='Azure:ActiveDirectory:Instance', value=''))
    # set_kvs.append(KeyValue(key='Azure:ActiveDirectory:TenantId', value=tenant_id))

    set_kvs.append(KeyValue(key='Azure:ResourceManager:ClientId', value=resource_manager_sp['appId']))
    set_kvs.append(KeyValue(key='Azure:ResourceManager:ClientSecret', value=resource_manager_sp['password']))
    # set_kvs.append(KeyValue(key='Azure:ResourceManager:Region', value=location.lower()))
    set_kvs.append(KeyValue(key='Azure:ResourceManager:TenantId', value=tenant_id))

    set_kvs.append(KeyValue(key='Azure:CosmosDb:ConnectionString', value=cosmosdb[1]))

    set_kvs.append(KeyValue(key='Azure:DeploymentStorage:ConnectionString', value=dep_storage[2]))

    for set_kv in set_kvs:
        azconfig_client.set_keyvalue(set_kv)


def _set_appconfig_orchestrator_keys(cli_ctx, subscription_id, appconfig, orchestrator, orchestrator_host_key):
    from azure.cli.command_modules.appconfig._azconfig.azconfig_client import AzconfigClient
    from azure.cli.command_modules.appconfig._azconfig.models import KeyValue

    azconfig_client = AzconfigClient(appconfig[2])

    set_kvs = []

    set_kvs.append(KeyValue(key='Orchestrator:Url', value='https://{}'.format(orchestrator.default_host_name)))
    set_kvs.append(KeyValue(key='Orchestrator:AuthCode', value=orchestrator_host_key))

    for set_kv in set_kvs:
        azconfig_client.set_keyvalue(set_kv)


def _create_api_app(cli_ctx, name, resource_group_name, location, appconfig, app_insights, tags=None):
    from azext_tc._client_factory import web_client_factory
    SkuDescription, AppServicePlan, SiteConfig, Site, NameValuePair, ConnStringInfo = get_sdk(
        cli_ctx, ResourceType.MGMT_APPSERVICE, 'SkuDescription', 'AppServicePlan', 'SiteConfig', 'Site', 'NameValuePair', 'ConnStringInfo', mod='models')

    web_client = web_client_factory(cli_ctx)

    sku_def = SkuDescription(tier='STANDARD', name='S1', capacity=None)
    plan_def = AppServicePlan(location=location, tags=tags, sku=sku_def,
                              reserved=None, hyper_v=None, name=name,
                              per_site_scaling=False, hosting_environment_profile=None)

    app_service_poller = web_client.app_service_plans.create_or_update(name=name, resource_group_name=resource_group_name, app_service_plan=plan_def)
    app_service = LongRunningOperation(cli_ctx)(app_service_poller)

    site_config = SiteConfig(app_settings=[], connection_strings=[])
    site_config.always_on = True

    site_config.connection_strings.append(ConnStringInfo(name='ConfigurationService', connection_string=appconfig[2]))

    site_config.app_settings.append(NameValuePair(name="WEBSITE_NODE_DEFAULT_VERSION", value='10.14'))
    site_config.app_settings.append(NameValuePair(name='ANCM_ADDITIONAL_ERROR_PAGE_LINK', value='https://{}.scm.azurewebsites.net/detectors'.format(name)))
    site_config.app_settings.append(NameValuePair(name='ApplicationInsightsAgent_EXTENSION_VERSION', value='~2'))

    if app_insights is not None and app_insights.instrumentation_key is not None:
        site_config.app_settings.append(NameValuePair(name='APPINSIGHTS_INSTRUMENTATIONKEY', value=app_insights.instrumentation_key))

    webapp_def = Site(location=location, site_config=site_config, server_farm_id=app_service.id, tags=tags)

    poller = web_client.web_apps.create_or_update(resource_group_name, name, webapp_def)
    webapp = LongRunningOperation(cli_ctx)(poller)

    return webapp


def _create_function_app(cli_ctx, name, resource_group_name, location, wj_storage, th_storage, appconfig=None, app_insights=None, tags=None):
    from azext_tc._client_factory import web_client_factory
    from azure.cli.core.util import send_raw_request
    SiteConfig, Site, NameValuePair, ConnStringInfo = get_sdk(
        cli_ctx, ResourceType.MGMT_APPSERVICE, 'SiteConfig', 'Site', 'NameValuePair', 'ConnStringInfo', mod='models')

    web_client = web_client_factory(cli_ctx)

    site_config = SiteConfig(app_settings=[], connection_strings=[])

    regions = web_client.list_geo_regions(sku='Dynamic')
    locations = [{'name': x.name.lower().replace(' ', '')} for x in regions]

    deploy_location = next((l for l in locations if l['name'].lower() == location.lower()), None)
    if deploy_location is None:
        raise CLIError(
            "Location is invalid. Use: az functionapp list-consumption-locations")

    if appconfig is not None:
        site_config.connection_strings.append(ConnStringInfo(name='ConfigurationService', connection_string=appconfig[2]))

    # adding appsetting to site to make it a function
    site_config.app_settings.append(NameValuePair(name='FUNCTIONS_EXTENSION_VERSION', value='~3'))
    site_config.app_settings.append(NameValuePair(name='AzureWebJobsStorage', value=wj_storage[2]))
    site_config.app_settings.append(NameValuePair(name='DurableFunctionsHubStorage', value=th_storage[2]))
    site_config.app_settings.append(NameValuePair(name='WEBSITE_NODE_DEFAULT_VERSION', value='~12'))
    site_config.app_settings.append(NameValuePair(name='WEBSITE_CONTENTAZUREFILECONNECTIONSTRING', value=wj_storage[2]))
    site_config.app_settings.append(NameValuePair(name='WEBSITE_CONTENTSHARE', value=name.lower()))
    site_config.app_settings.append(NameValuePair(name='FUNCTION_APP_EDIT_MODE', value='readonly'))

    if app_insights is not None and app_insights.instrumentation_key is not None:
        site_config.app_settings.append(NameValuePair(name='APPINSIGHTS_INSTRUMENTATIONKEY', value=app_insights.instrumentation_key))

    functionapp_def = Site(location=None, site_config=site_config, tags=tags)
    functionapp_def.location = location
    functionapp_def.kind = 'functionapp'

    poller = web_client.web_apps.create_or_update(resource_group_name, name, functionapp_def)
    functionapp = LongRunningOperation(cli_ctx)(poller)

    admin_token = web_client.web_apps.get_functions_admin_token(resource_group_name, name)

    host_key_url = 'https://{}/admin/host/keys/default'.format(functionapp.default_host_name)
    host_key_auth_header = 'Authorization=Bearer {}'.format(admin_token)

    host_key_response = send_raw_request(cli_ctx, 'GET', host_key_url, [host_key_auth_header], skip_authorization_header=True)
    host_key_json = host_key_response.json()
    host_key = host_key_json['value']

    return functionapp, host_key


def _try_create_application_insights(cli_ctx, name, resource_group_name, location):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.mgmt.applicationinsights import ApplicationInsightsManagementClient
    creation_failed_warn = 'Unable to create the Application Insights for the Function App. ' \
                           'Please use the Azure Portal to manually create and configure the Application Insights, ' \
                           'if needed.'

    app_insights_client = get_mgmt_service_client(cli_ctx, ApplicationInsightsManagementClient)
    properties = {
        "name": name,
        "location": location,
        "kind": "web",
        "properties": {
            "Application_Type": "web"
        }
    }

    appinsights = app_insights_client.components.create_or_update(resource_group_name, name, properties)

    if appinsights is None or appinsights.instrumentation_key is None:
        logger.warning(creation_failed_warn)
        return None

    # We make this success message as a warning to no interfere with regular JSON output in stdout
    logger.warning('Application Insights \"%s\" was created for this TeamCloud instance. '
                   'You can visit https://portal.azure.com/#resource%s/overview to view your '
                   'Application Insights component', appinsights.name, appinsights.id)

    return appinsights


def _create_keyvault(cli_ctx, name, resource_group_name, location):
    pass


def _create_resource_manager_sp(cmd):
    from azure.cli.command_modules.role.custom import create_service_principal_for_rbac, add_permission, admin_consent

    sp = create_service_principal_for_rbac(cmd, name='http://TeamCloud.ResourceManager', years=10, role='Owner')

    add_permission(cmd, identifier=sp['appId'], api='00000002-0000-0000-c000-000000000000', api_permissions=['5778995a-e1bf-45b8-affa-663a9f3f4d04=Role'])

    add_permission(cmd, identifier=sp['appId'], api='00000003-0000-0000-c000-000000000000', api_permissions=[
        'e1fe6dd8-ba31-4d61-89e7-88639da4683d=Scope',
        '7ab1d382-f21e-4acd-a863-ba3e13f7da61=Role',
        'df021288-bdef-4463-88db-98f22de89214=Role'])

    admin_consent(cmd, identifier=sp['appId'])

    return sp


def _deploy_app(cli_ctx, resource_group_name, name, location, repo_url, slot=None, app_instance=None):
    from azure.mgmt.web.models import SiteSourceControl
    from azext_tc._client_factory import web_client_factory

    web_client = web_client_factory(cli_ctx).web_apps

    source_control = SiteSourceControl(location=location, repo_url=repo_url, branch='master',
                                       is_manual_integration=True, is_mercurial=False)

    # SCC config can fail if previous commands caused SCMSite shutdown, so retry here.
    for i in range(5):
        try:
            poller = web_client.create_or_update_source_control(resource_group_name, name, source_control)

            return LongRunningOperation(cli_ctx)(poller)
        except Exception as ex:  # pylint: disable=broad-except
            import re
            # for non server errors(50x), just throw; otherwise retry 4 times
            if i == 4 or not re.findall(r'\(50\d\)', str(ex)):
                raise
            logger.warning('retrying %s/4', i + 1)
            sleep(5)   # retry in a moment


def _zip_deploy_app(cli_ctx, resource_group_name, name, repo_url, zip_name, version=None, slot=None, app_instance=None, timeout=None):
    from azure.cli.core.util import should_disable_connection_verify
    from azext_tc._client_factory import web_client_factory

    web_client = web_client_factory(cli_ctx).web_apps

    #  work around until the timeout limits issue for linux is investigated & fixed
    creds = web_client.list_publishing_credentials(resource_group_name, name)
    creds = creds.result()

    try:
        scm_url = _get_scm_url(cli_ctx, resource_group_name, name, slot=slot, app_instance=app_instance)
    except ValueError:
        raise CLIError('Failed to fetch scm url for azure app service app')

    zipdeploy_url = scm_url + '/api/zipdeploy?isAsync=true'
    deployment_status_url = scm_url + '/api/deployments/latest'

    import requests
    import urllib3

    authorization = urllib3.util.make_headers(basic_auth='{}:{}'.format(creds.publishing_user_name, creds.publishing_password))

    zip_package_uri = '{}/releases/latest/download/{}.zip'.format(repo_url, zip_name)

    if version:
        version = version.lower()
        from re import match
        m = match(r'^[vV]?[0-9]+\.[0-9]+\.[0-9]+$', version)
        if m is None:
            raise CLIError('--version should be in format v0.0.0 do not include -pre suffix')

        zip_package_uri = '{}/releases/download/{}/{}.zip'.format(repo_url, version, zip_name)

    logger.warning("Starting zip deployment. This will take several minutes to complete...")
    res = requests.put(zipdeploy_url, headers=authorization, json={'packageUri': zip_package_uri}, verify=not should_disable_connection_verify())

    # check if there's an ongoing process
    if res.status_code == 409:
        raise CLIError("There may be an ongoing deployment or your app setting has WEBSITE_RUN_FROM_PACKAGE. "
                       "Please track your deployment in {} and ensure the WEBSITE_RUN_FROM_PACKAGE app setting "
                       "is removed.".format(deployment_status_url))

    # check the status of async deployment
    response = _check_zip_deployment_status(cli_ctx, resource_group_name, name, deployment_status_url, authorization, slot=slot, app_instance=app_instance, timeout=timeout)

    return response


def _check_zip_deployment_status(cli_ctx, resource_group_name, name, deployment_status_url, authorization, slot=None, app_instance=None, timeout=None):
    import json
    import requests
    from azure.cli.core.util import should_disable_connection_verify
    total_trials = (int(timeout) // 2) if timeout else 450
    num_trials = 0
    while num_trials < total_trials:
        sleep(2)
        response = requests.get(deployment_status_url, headers=authorization, verify=not should_disable_connection_verify())
        sleep(2)
        try:
            res_dict = response.json()
        except json.decoder.JSONDecodeError:
            logger.warning("Deployment status endpoint %s returned malformed data. Retrying...", deployment_status_url)
            res_dict = {}
        finally:
            num_trials = num_trials + 1

        if res_dict.get('status', 0) == 3:
            _configure_default_logging(cli_ctx, resource_group_name, name, slot=slot, app_instance=app_instance)
            raise CLIError("Zip deployment failed. {}. Please run the command az webapp log tail -n {} -g {}".format(res_dict, name, resource_group_name))
        if res_dict.get('status', 0) == 4:
            break
        if 'progress' in res_dict:
            logger.info(res_dict['progress'])  # show only in debug mode, customers seem to find this confusing
    # if the deployment is taking longer than expected
    if res_dict.get('status', 0) != 4:
        _configure_default_logging(cli_ctx, resource_group_name, name, slot=slot, app_instance=app_instance)
        raise CLIError("Timeout reached by the command, however, the deployment operation is still on-going. Navigate to your scm site to check the deployment status")
    return res_dict


# TODO: expose new blob suport
def _configure_default_logging(cli_ctx, resource_group_name, name, slot=None, app_instance=None, level=None,
                               web_server_logging='filesystem', docker_container_logging='true'):
    logger.warning("Configuring default logging for the app, if not already enabled...")
    from azure.mgmt.web.models import (FileSystemApplicationLogsConfig, ApplicationLogsConfig,
                                       SiteLogsConfig, HttpLogsConfig, FileSystemHttpLogsConfig)

    site = _get_webapp(cli_ctx, resource_group_name, name, slot=slot, app_instance=app_instance)

    location = site.location

    fs_log = FileSystemApplicationLogsConfig(level='Error')
    application_logs = ApplicationLogsConfig(file_system=fs_log)

    http_logs = None
    server_logging_option = web_server_logging or docker_container_logging
    if server_logging_option:
        # TODO: az blob storage log config currently not in use, will be impelemented later.
        # Tracked as Issue: #4764 on Github
        filesystem_log_config = None
        turned_on = server_logging_option != 'off'
        if server_logging_option in ['filesystem', 'off']:
            # 100 mb max log size, retention lasts 3 days. Yes we hard code it, portal does too
            filesystem_log_config = FileSystemHttpLogsConfig(retention_in_mb=100, retention_in_days=3, enabled=turned_on)

        http_logs = HttpLogsConfig(file_system=filesystem_log_config, azure_blob_storage=None)

    site_log_config = SiteLogsConfig(location=location,
                                     application_logs=application_logs,
                                     http_logs=http_logs,
                                     failed_requests_tracing=None,
                                     detailed_error_messages=None)

    from azext_tc._client_factory import web_client_factory
    web_client = web_client_factory(cli_ctx).web_apps

    return web_client.update_diagnostic_logs_config(resource_group_name, name, site_log_config)


def _get_scm_url(cli_ctx, resource_group_name, name, slot=None, app_instance=None):
    from azure.mgmt.web.models import HostType
    webapp = _get_webapp(cli_ctx, resource_group_name, name, slot=slot, app_instance=app_instance)
    for host in webapp.host_name_ssl_states or []:
        if host.host_type == HostType.repository:
            return "https://{}".format(host.name)


def _get_webapp(cli_ctx, resource_group_name, name, slot=None, app_instance=None):
    webapp = app_instance
    if not app_instance:
        from azext_tc._client_factory import web_client_factory
        web_client = web_client_factory(cli_ctx).web_apps
        webapp = web_client.get(resource_group_name, name)
    if not webapp:
        raise CLIError("'{}' app doesn't exist".format(name))

    # Should be renamed in SDK in a future release
    try:
        setattr(webapp, 'app_service_plan_id', webapp.server_farm_id)
        del webapp.server_farm_id
    except AttributeError:
        pass

    return webapp
