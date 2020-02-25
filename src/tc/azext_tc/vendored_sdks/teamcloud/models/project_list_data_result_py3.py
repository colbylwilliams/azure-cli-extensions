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


class ProjectListDataResult(Model):
    """ProjectListDataResult.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :param code:
    :type code: int
    :param status:
    :type status: str
    :ivar data:
    :vartype data: list[~teamcloud.models.Project]
    :param location:
    :type location: str
    """

    _validation = {
        'data': {'readonly': True},
    }

    _attribute_map = {
        'code': {'key': 'code', 'type': 'int'},
        'status': {'key': 'status', 'type': 'str'},
        'data': {'key': 'data', 'type': '[Project]'},
        'location': {'key': 'location', 'type': 'str'},
    }

    def __init__(self, *, code: int=None, status: str=None, location: str=None, **kwargs) -> None:
        super(ProjectListDataResult, self).__init__(**kwargs)
        self.code = code
        self.status = status
        self.data = None
        self.location = location
