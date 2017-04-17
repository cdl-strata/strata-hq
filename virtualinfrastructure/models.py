from django.db import models
from management.models import Site, Team
from infrastructure.models import Asset, GeneralServer

# Hypervisors - Oracle OVM, VMWare ESXi 6 etc...
class Hypervisor(models.Model):
    vendor = models.CharField(max_length=64)
    product = models.CharField(max_length=32)
    description = models.CharField(max_length=64, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return '%s - %s %s' % (self.vendor, self.product, self.description)

# We use this as a sort of proxy class
class VirtualComponentAbstract(models.Model):
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=(('server', 'Server'),('pool', 'Pool')))
    hypervisor = models.ForeignKey('Hypervisor')

    def __str__(self):
        return '%s: %s' % (self.type.capitalize(), self.name)

    class Meta:
        ordering = ['type', 'name']

# Virtual Data Centers - a logical group of VM's - This might span DC's / Physical sites.
class VirtualServerPool(VirtualComponentAbstract):
    site = models.ManyToManyField(Site)
    hosts = models.ManyToManyField('VirtualServerHost')

    def __str__(self):
        return self.name

class VirtualServerHost(VirtualComponentAbstract):
    physical_server = models.OneToOneField(Asset, limit_choices_to={'vm_host': True})

    def __str__(self):
        return self.physical_server.name

    def save(self, *args, **kwargs):
        # Fix up serialnumber
        self.name = self.physical_server.name

        super(VirtualServerHost, self).save(*args, **kwargs)

class VirtualServer(GeneralServer):
    running_on = models.ForeignKey('VirtualComponentAbstract')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Fix up serialnumber
        self.is_virtual = True

        super(VirtualServer, self).save(*args, **kwargs)