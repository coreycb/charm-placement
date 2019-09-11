# Overview

This charm provides the Placement service for an OpenStack Cloud.

OpenStack Train or later is required.

# Usage

Placement relies on mysql, keystone, and nova-cloud-controller charms:

    juju deploy --series bionic --config openstack-origin=cloud:bionic-train cs:placement
    juju add-relation placement mysql
    juju add-relation placement keystone
    juju add-relation placement nova-cloud-controller

If upgrading nova-cloud-controller to Train, the placement charm must first be deployed
for Train and related to the Stein-based nova-cloud-controller. Once the placement charm
is fully deployed for Train (new endpoints registered and instances can successfully
launch), nova-cloud-controller can then be upgraded to Train:

    juju deploy --series bionic --config openstack-origin=cloud:bionic-train cs:placement
    juju add-relation placement mysql
    juju add-relation placement keystone
    juju add-relation placement nova-cloud-controller
    juju config nova-cloud-controller openstack-origin=cloud:bionic-train

# Bugs

Please report bugs on [Launchpad](https://bugs.launchpad.net/charm-placement/+filebug).

For general questions please refer to the OpenStack [Charm Guide](https://docs.openstack.org/charm-guide/latest/).
