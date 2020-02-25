# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from collections import OrderedDict
# from knack.util import CLIError
from knack.log import get_logger
from azext_tc.vendored_sdks.teamcloud.models import (ErrorResult, StatusResult)

logger = get_logger(__name__)


def transform_output(result):
    if isinstance(result, ErrorResult):
        return transform_error(result)

    if isinstance(result, StatusResult):
        return transform_status(result)

    logger.warning(result.__dict__)

    try:
        return result.data
    except AttributeError:
        logger.warning('nope')
        return None


def transform_error(result):
    logger.error('Error: {}'.format(result.status))
    return result


def transform_status(result):
    return result

# ----------------
# TeamCloud Users
# ----------------


def transform_user_table_output(result):
    if not isinstance(result, list):
        result = [result]

    resultList = []

    for item in result:
        resultList.append(OrderedDict([
            ('User ID', item['id']),
            ('Role', item['role']),
            ('Tags', str(item['tags']))
        ]))

    return resultList

# ----------------
# Projects
# ----------------


def transform_project_table_output(result):
    if not isinstance(result, list):
        result = [result]

    resultList = []

    for item in result:
        resultList.append(OrderedDict([
            ('Project ID', item['id']),
            ('Name', item['name']),
            ('Type', item['type']['id']),
            ('Resource Group', item['resourceGroup']['resourceGroupName']),
            ('Subscription', item['resourceGroup']['subscriptionId']),
            ('Region', item['resourceGroup']['region']),
            ('Tags', str(item['tags'])),
            ('Properties', str(item['properties']))
        ]))

    return resultList

# ----------------
# Project Users
# ----------------

# ----------------
# Project Types
# ----------------


def transform_project_type_table_output(result):
    if not isinstance(result, list):
        result = [result]

    resultList = []

    for item in result:
        resultList.append(OrderedDict([
            ('Project Type ID', item['id']),
            ('Default', item['default']),
            ('Region', item['region']),
            ('Subscriptions', '\n'.join(item['subscriptions'])),
            ('Subscription Capacity', item['subscriptionCapacity']),
            ('Resource Group Prefix', item['resourceGroupNamePrefix']),
            ('Providers', '\n'.join([p['id'] for p in item['providers']])),
            ('Tags', str(item['tags'])),
            ('Properties', str(item['properties']))
        ]))

    return resultList

# ----------------
# Providers
# ----------------


def transform_provider_table_output(result):
    if not isinstance(result, list):
        result = [result]

    resultList = []

    for item in result:
        resultList.append(OrderedDict([
            ('Provider ID', item['id']),
            ('Url', item['url']),
            ('Code', '************'),
            ('Optional', item['optional']),
            ('Dependencies (Create)', '\n'.join(
                item['dependencies']['create'])),
            ('Dependencies (Init)', '\n'.join(item['dependencies']['init'])),
            ('Events', '\n'.join(item['events'])),
            ('Properties', str(item['properties'])),
            # ('Tags', str(item['tags'])),
            # ('Properties', '\n'.join(["'{}': '{}'".format(k, v) for k, v in item['properties'].items()]))
        ]))

    return resultList
