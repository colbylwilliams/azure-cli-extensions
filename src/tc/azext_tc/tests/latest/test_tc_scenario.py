# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest

from azure_devtools.scenario_tests import AllowLargeResponse
from azure.cli.testsdk import (ScenarioTest, ResourceGroupPreparer)


TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..'))


# class TeamCloudLiveScenarioTest(LiveScenarioTest):

#     def test_tc_project(self):
#         self.kwargs.update({
#             'url': 'http://localhost:5001',
#             'name': self.create_random_name(prefix='cli', length=10)
#         })

#         project_name = self.create_random_name(prefix='cli', length=10)

#         self.cmd('az tc project create -u {url} -n {name} --tags foo=bar', checks=[
#             self.check('tags.foo', 'bar'),
#             self.check('name', '{name}')
#         ]

class TeamCloudScenarioTest(ScenarioTest):

    @ResourceGroupPreparer(name_prefix='CLI_TESTS_', parameter_name_for_location='location')
    def test_tc(self, resource_group, location):
        self.kwargs.update({
            'name': 'test1',
            'loc': location
        })

        self.cmd('tc create -g {rg} -n {name} --tags foo=doo', checks=[
            self.check('tags.foo', 'doo'),
            self.check('name', '{name}')
        ])
        self.cmd('tc update -g {rg} -n {name} --tags foo=boo', checks=[
            self.check('tags.foo', 'boo')
        ])
        count = len(self.cmd('tc list').get_output_in_json())
        self.cmd('tc show - {rg} -n {name}', checks=[
            self.check('name', '{name}'),
            self.check('resourceGroup', '{rg}'),
            self.check('tags.foo', 'boo')
        ])
        self.cmd('tc delete -g {rg} -n {name}')
        final_count = len(self.cmd('tc list').get_output_in_json())
        self.assertTrue(final_count, count - 1)
