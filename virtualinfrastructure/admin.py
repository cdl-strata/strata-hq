from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
from .models import Hypervisor, VirtualServerPool, VirtualServerHost, VirtualServer

@admin.register(Hypervisor)
class HypervisorAdmin(admin.ModelAdmin):
    pass

@admin.register(VirtualServerPool)
class VirtualServerPoolAdmin(admin.ModelAdmin):
    pass

@admin.register(VirtualServerHost)
class VirtualServerHostAdmin(admin.ModelAdmin):
    pass

@admin.register(VirtualServer)
class VirtualServerAdmin(admin.ModelAdmin):
    pass