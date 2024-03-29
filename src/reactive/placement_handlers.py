# Copyright 2019 Canonical Ltd
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

import charms_openstack.bus
charms_openstack.bus.discover()

import charms_openstack.charm
import charms.reactive as reactive


charms_openstack.charm.use_defaults(
    'charm.installed',
    'shared-db.connected',
    'identity-service.connected',
    'identity-service.available',
    'config.changed',
    'update-status',
    'upgrade-charm',
    'certificates.available',
)


@reactive.when('shared-db.available')
@reactive.when('identity-service.available')
def render_config(*args):
    with charms_openstack.charm.provide_charm_instance() as placement_charm:
        placement_charm.render_with_interfaces(args)
        placement_charm.assess_status()
    reactive.set_state('config.rendered')


@reactive.when('config.rendered')
@reactive.when('placement.available')
@reactive.when_not('db.synced')
def init_db(placement):
    with charms_openstack.charm.provide_charm_instance() as placement_charm:
        placement = reactive.endpoint_from_flag('placement.available')
        disabled = placement.get_nova_placement_disabled()
        if disabled:
            placement_charm.disable_services()
            placement_charm.db_migrate()
            placement_charm.db_sync()
            placement_charm.enable_services()
            placement_charm.assess_status()
            placement.set_placement_enabled()
            reactive.set_state('db.synced')


@reactive.when('ha.connected')
def cluster_connected(hacluster):
    """Configure HA resources in corosync"""
    with charms_openstack.charm.provide_charm_instance() as placement_charm:
        placement_charm.configure_ha_resources(hacluster)
        placement_charm.assess_status()
