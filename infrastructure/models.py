from django.db import models
from django.db.models import Count
from titlecase import titlecase
from django.contrib.auth.models import User
from cuser.middleware import CuserMiddleware
from management.models import Team, Site

import socket

_statuses = (('needs-setup', 'Ready to be set up'),
             ('installed', 'Installed'),
             ('cold-standby', 'Cold Standby'),
             ('hot-standby', 'Hot standby'),
             ('live', 'Live system'),
             ('puppet_devel', 'Puppet Development machine'),
             ('spare', 'Spare machine'),
             ('obsolete', 'Obsolete'),
             ('decommissioned', 'Decommissioned'),
             ('broken', 'Awaiting repair'))

_operating_systems = (('centos6', 'CentOS 6'),
                      ('centos7', 'CentOS 7'),
                      ('oel6', 'Oracle Enterprise Linux 6'),
                      ('oel7', 'Oracle Enterprise Linux 7'),
                      ('rhel6', 'Red Hat Enterprise Linux 6'),
                      ('rhel7', 'Red Hat Enterprise Linux 7'),
                      ('vmware', 'VMWare ESXi'),
                      ('windows2k3', 'Windows Server 2003'),
                      ('windows2k8', 'Windows Server 2008'),
                      ('windows2k12', 'Windows Server 2012'),
                      ('windowscore', 'Windows Server Core'))

# Asset is a base class which has common fields for abstract classes such as a server (bare metal) a virtual server,
# a network switch or a storage device.
class Asset(models.Model):
    """Base class for all our hardware assets"""
    name = models.CharField(max_length=128, db_index=True,
                            help_text='Examples: "uat-hdc-app001", "sdc-core-fw002" or "B056')
    description = models.CharField(max_length=32, blank=True)
    owner = models.ForeignKey(Team)
    site = models.ForeignKey(Site)
    status = models.CharField(max_length=16, choices=_statuses, default='needs-setup')
    serialnumber = models.CharField(max_length=64, blank=True)
    support_contract = models.CharField(max_length=64, blank=True)
    support_contract_end = models.DateTimeField(blank=True,null=True)
    is_virtual = models.BooleanField(default=False)
    vm_host = models.BooleanField(default=False)
    last_edit = models.DateTimeField(auto_now=True)
    last_editor = models.ForeignKey(User, editable=False)
    notes = models.TextField(max_length=1024, blank=True)

    class Meta:
        # Assets *could* have the same name (probably shouldn't) but they should at least be unique per site
        unique_together = (('name', 'site'),)
        ordering = ('name',)

    def __str__(self):
        return '%s' % (self.name,)

    def save(self, *args, **kwargs):
        # Fix up serialnumber
        self.serialnumber = self.serialnumber.upper()

        # Fix up hostname
        self.name = self.name.lower()

        # Set the last edited user
        user = CuserMiddleware.get_user()
        self.last_editor = user

        super(Asset, self).save(*args, **kwargs)


# Racks - Server / Network racks and frames. Examples: FR01, RA056,
class Rack(Asset):
    """Model for racks or frames"""
    manufacturer = models.CharField(max_length=64, blank=True)
    rack_or_frame = models.CharField(max_length=16, choices=(('rack', 'Rack'),
                                                             ('frame', 'Frame')))
    units = models.SmallIntegerField(help_text='Number of units available in this rack or frame')

    def __str__(self):
        return '%s/%s' % (self.site.name, self.name)

    class Meta:
        ordering = ('site__name', 'name')


# Racked Asset - Base class for assets that live in racks such as servers, switches, ups's, san's
class RackedAsset(Asset):
    """Base class for assets that live in racks"""
    in_rack = models.ForeignKey('Rack', blank=True, null=True)
    position = models.PositiveSmallIntegerField(blank=True, null=True,
                                                help_text='Top rack unit of asset. 0 for assets that aren\'t racked'
                                                          'but live in the rack')

    def save(self, *args, **kwargs):
        self.site = self.rack.site
        super(RackedAsset, self).save(*args, **kwargs)


# Hardware Meta - Shared metadata for to describe various hardware makes / models
class HardwareMeta(models.Model):
    manufacturer = models.CharField(max_length=64)
    model_name_or_number = models.CharField(max_length=64)

    def __str__(self):
        return '%s(%s)' % (self.model_name_or_number, self.manufacturer)

    def save(self, *args, **kwargs):
        self.model_name_or_number = self.model_name_or_number.upper()
        self.manufacturer = titlecase(self.manufacturer)
        super(HardwareMeta, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class RackedHardwareMeta(HardwareMeta):
    units = models.PositiveSmallIntegerField(default=1,
                                             help_text='Number of rack or blade units consumed by the asset')

    class Meta:
        abstract = True


# Blade Chassis extra manufacturer data
class BladeChassisModel(RackedHardwareMeta):
    blade_capacity = models.PositiveSmallIntegerField(default=16,
                                                      help_text='Number of blades this chassis can take')
BladeChassisModel._meta.get_field('units').default = 10


# Server manufacturer extra data
class ServerModel(HardwareMeta):
    pass


class RackedServerModel(RackedHardwareMeta):
    pass


# Server Role - Strata, Assentis, LoadBalancer, XMLGateway
class ServerRole(models.Model):
    name = models.CharField(max_length=64,
                            help_text='Descriptive name for the server role. Examples: "Strata Server" or "Load Balancer"')
    short_name = models.CharField(max_length=16,
                                  help_text='Short name for role. Examples: "app", "lb" or "web"')
    description = models.CharField(max_length=512)
    config_role_class = models.CharField(max_length=64, blank=True,
                                         help_text='Config management class. Example: "role::app" or "role::ass"')

    def __str__(self):
        return self.name


# Environment - dev, uat, prd
class Environment(models.Model):
    name = models.CharField(max_length=128, unique=True)
    short_name = models.CharField(max_length=5)
    api_proxy = models.CharField(max_length=1024, help_text='Example: http://apiprx:3000')
    api_proxy_ssl = models.BooleanField(default=True, verbose_name='SSL')
    agent_tag = models.CharField(max_length=64, default='none')

    def __str__(self):
        return self.name


# Domain - cdluat.local, cheshdatasys.co.uk, example.com
class Domain(models.Model):
    name = models.CharField(max_length=256)


# Blade Chassis
class BladeChassis(RackedAsset):
    model = models.ForeignKey('BladeChassisModel')

    class Meta:
        verbose_name_plural = 'Blade chassis'


# Rack Servers
class RackServer(RackedAsset):
    os = models.CharField(max_length=32, choices=_operating_systems)
    model = models.ForeignKey('RackedServerModel')
    domain = models.ForeignKey('Domain')
    role = models.ForeignKey('ServerRole')
    environment = models.ForeignKey('Environment')


# General non-rackable servers.
class GeneralServer(Asset):
    os = models.CharField(max_length=32, choices=_operating_systems)
    model = models.ForeignKey('ServerModel')
    domain = models.ForeignKey('Domain')
    role = models.ForeignKey('ServerRole')
    environment = models.ForeignKey('Environment')


# Blade Servers - lives in a chassis which lives in a rack.
class BladeServer(GeneralServer):
    chassis = models.ForeignKey('BladeChassis', related_name='blade_chassis')
    blade_position = models.PositiveIntegerField(default=1)

