# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import print_function

import mock

import reactive.placement_handlers as handlers

import charms_openstack.test_utils as test_utils


class TestRegisteredHooks(test_utils.TestRegisteredHooks):

    def test_hooks(self):
        defaults = [
            'charm.installed',
            'shared-db.connected',
            'identity-service.connected',
            'identity-service.available',
            'config.changed',
            'update-status',
            'upgrade-charm',
            'certificates.available']
        hook_set = {
            'when': {
                'render_config': ('shared-db.available',
                                  'identity-service.available',),
                'init_db': ('config.rendered',
                            'placement.connected',),
                'cluster_connected': ('ha.connected',),
            },
            'when_not': {
                'init_db': ('db.synced',),
            },
        }
        # test that the hooks were registered via the
        # reactive.barbican_handlers
        self.registered_hooks_test_helper(handlers, hook_set, defaults)

class TestPlacementHandlers(test_utils.PatchHelper):

    def setUp(self):
        super().setUp()
        self.placement_charm = mock.MagicMock()
        self.patch_object(handlers.charm, 'provide_charm_instance',
                          new=mock.MagicMock())
        self.provide_charm_instance().__enter__.return_value = self.placement_charm
        self.provide_charm_instance().__exit__.return_value = None

    def test_render_config(self):
        self.patch_object(handlers.reactive, 'set_state')
        handlers.render_config('arg1', 'arg2')
        self.placement_charm.render_with_interfaces.assert_called_once_with(
                ('arg1', 'arg2'))
        self.placement_charm.assess_status.assert_called_once_with()
        self.set_state.assert_called_once_with('config.rendered')


    def test_init_db(self):
        self.patch_object(handlers.reactive, 'set_state')
        self.placement_charm.get_nova_placement_disabled.return_value = True
        handlers.init_db(self.placement_charm)
        self.placement_charm.disable_services.assert_called_once_with()
        self.placement_charm.db_migrate.assert_called_once_with()
        self.placement_charm.db_sync.assert_called_once_with()
        self.placement_charm.enable_services.assert_called_once_with()
        self.placement_charm.assess_status.assert_called_once_with()
        self.placement_charm.set_placement_enabled.assert_called_once_with()
        self.set_state.assert_called_once_with('db.synced')

    def test_cluster_connected(self):
        hacluster = mock.MagicMock()
        handlers.cluster_connected(hacluster)
        self.placement_charm.configure_ha_resources.assert_called_once_with(
            hacluster)
        self.placement_charm.assess_status.assert_called_once_with()
