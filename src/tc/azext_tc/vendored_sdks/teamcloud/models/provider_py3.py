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


class Provider(Model):
    """Provider.

    :param id:
    :type id: str
    :param url:
    :type url: str
    :param auth_code:
    :type auth_code: str
    :param principal_id:
    :type principal_id: str
    :param optional:
    :type optional: bool
    :param dependencies:
    :type dependencies: ~teamcloud.models.ProviderDependenciesModel
    :param events:
    :type events: list[str]
    :param properties:
    :type properties: dict[str, str]
    :param registered:
    :type registered: datetime
    """

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'url': {'key': 'url', 'type': 'str'},
        'auth_code': {'key': 'authCode', 'type': 'str'},
        'principal_id': {'key': 'principalId', 'type': 'str'},
        'optional': {'key': 'optional', 'type': 'bool'},
        'dependencies': {'key': 'dependencies', 'type': 'ProviderDependenciesModel'},
        'events': {'key': 'events', 'type': '[str]'},
        'properties': {'key': 'properties', 'type': '{str}'},
        'registered': {'key': 'registered', 'type': 'iso-8601'},
    }

    def __init__(self, *, id: str=None, url: str=None, auth_code: str=None, principal_id: str=None, optional: bool=None, dependencies=None, events=None, properties=None, registered=None, **kwargs) -> None:
        super(Provider, self).__init__(**kwargs)
        self.id = id
        self.url = url
        self.auth_code = auth_code
        self.principal_id = principal_id
        self.optional = optional
        self.dependencies = dependencies
        self.events = events
        self.properties = properties
        self.registered = registered
