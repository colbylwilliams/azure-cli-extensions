# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class AzureResourceGroup(Model):
    """AzureResourceGroup.

    :param resource_group_id:
    :type resource_group_id: str
    :param resource_group_name:
    :type resource_group_name: str
    :param subscription_id:
    :type subscription_id: str
    :param region:
    :type region: str
    """

    _attribute_map = {
        'resource_group_id': {'key': 'resourceGroupId', 'type': 'str'},
        'resource_group_name': {'key': 'resourceGroupName', 'type': 'str'},
        'subscription_id': {'key': 'subscriptionId', 'type': 'str'},
        'region': {'key': 'region', 'type': 'str'},
    }

    def __init__(self, *, resource_group_id: str=None, resource_group_name: str=None, subscription_id: str=None, region: str=None, **kwargs) -> None:
        super(AzureResourceGroup, self).__init__(**kwargs)
        self.resource_group_id = resource_group_id
        self.resource_group_name = resource_group_name
        self.subscription_id = subscription_id
        self.region = region
