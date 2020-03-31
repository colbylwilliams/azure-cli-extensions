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

    @ResourceGroupPreparer(parameter_name='tc_group', parameter_name_for_location='location', location='eastus')
    @ResourceGroupPreparer(parameter_name='provider_group', location='eastus')
    def test_tc(self, tc_group, provider_group, location):

        pre_version = 'v0.1.274'
        provider_pre_version = 'v0.1.9'

        subscription = self.current_subscription()
        tc_name = self.create_random_name(prefix='cli', length=11)

        cmd = 'tc create -n {name} -g {tc_group} -l {location} -v {pre_version}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['location'], location)
        self.assertEqual(result['version'], pre_version)
        self.assertIsNotNone(result['base_url'])

        base_url = result['base_url']

        provider = 'azure.appinsights'
        cmd = 'tc provider deploy -u {base_url} -n {provider} -g {provider_group} -v {provider_pre_version}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['id'], provider)
        self.assertIsNotNone(result['url'])

        cmd = 'tc provider show -u {base_url} -n {provider}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(result['id'], provider)
        self.assertIsNotNone(result['url'])

        cmd = 'tc provider list -u {base_url}'.format(**locals())
        result = self.cmd(cmd).get_output_in_json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], provider)
        self.assertIsNotNone(result[0]['url'])

