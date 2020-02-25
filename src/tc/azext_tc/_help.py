# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from knack.help_files import helps  # pylint: disable=unused-import


helps['tc'] = """
    type: group
    short-summary: Commands to manage a TeamCloud instance.
"""


# ----------------
# TeamCloud Users
# ----------------

helps['tc user'] = """
    type: group
    short-summary: Commands to manage Users for a TeamCloud instance.
"""

helps['tc user create'] = """
    type: command
    short-summary: Create a new User in the TeamCloud instance.
"""

helps['tc user delete'] = """
    type: command
    short-summary: Delete a User from the TeamCloud instance.
"""

helps['tc user list'] = """
    type: command
    short-summary: List Users in the TeamCloud instance.
"""

helps['tc user show'] = """
    type: command
    short-summary: Show the details of a User in the TeamCloud instance.
"""

# ----------------
# Projects
# ----------------

helps['tc project'] = """
    type: group
    short-summary: Commands to manage Projects for a TeamCloud instance.
"""

helps['tc project create'] = """
    type: command
    short-summary: Create a new Project in the TeamCloud instance.
"""

helps['tc project delete'] = """
    type: command
    short-summary: Delete a Project from the TeamCloud instance.
"""

helps['tc project list'] = """
    type: command
    short-summary: List Projects in the TeamCloud instance.
"""

helps['tc project show'] = """
    type: command
    short-summary: Show the details of a Project in the TeamCloud instance.
"""

# ----------------
# Project Users
# ----------------

helps['tc project user'] = """
    type: group
    short-summary: Commands to manage Users for a Project.
"""

helps['tc project user create'] = """
    type: command
    short-summary: Create a new User in a Project.
"""

helps['tc project user delete'] = """
    type: command
    short-summary: Delete a User from a Project.
"""

helps['tc project user list'] = """
    type: command
    short-summary: List Users in a Project.
"""

helps['tc project user show'] = """
    type: command
    short-summary: Show the details of a User in a Project.
"""

# ----------------
# Project Types
# ----------------

helps['tc project-type'] = """
    type: group
    short-summary: Commands to manage Project Types for a TeamCloud instance.
"""

helps['tc project-type create'] = """
    type: command
    short-summary: Create a new Project Type in the TeamCloud instance.
"""

helps['tc project-type delete'] = """
    type: command
    short-summary: Delete a Project Type from the TeamCloud instance.
"""

helps['tc project-type list'] = """
    type: command
    short-summary: List Project Types in the TeamCloud instance.
"""

helps['tc project-type show'] = """
    type: command
    short-summary: Show the details of a Project Type in the TeamCloud instance.
"""

# ----------------
# Providers
# ----------------

helps['tc provider'] = """
    type: group
    short-summary: Commands to manage Providers for a TeamCloud instance.
"""

helps['tc provider create'] = """
    type: command
    short-summary: Create a new Provider in the TeamCloud instance.
"""

helps['tc provider delete'] = """
    type: command
    short-summary: Delete a Provider from the TeamCloud instance.
"""

helps['tc provider list'] = """
    type: command
    short-summary: List Providers in the TeamCloud instance.
"""

helps['tc provider show'] = """
    type: command
    short-summary: Show the details of a Provider in the TeamCloud instance.
"""

# ----------------
# Status
# ----------------
