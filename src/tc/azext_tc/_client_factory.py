# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


def cf_tc(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_tc.vendored_sdks.teamcloud import TeamCloudClient
    return get_mgmt_service_client(cli_ctx, TeamCloudClient, subscription_bound=False, base_url_bound=False)
