from django.contrib import admin

from .models import Asset, Rack, BladeChassisModel, BladeChassis, BladeServer, RackServer, GeneralServer, \
    ServerModel, ServerRole, Domain, Environment


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    pass


@admin.register(BladeChassisModel)
class BladeChassisModelAdmin(admin.ModelAdmin):
    pass


@admin.register(BladeChassis)
class BladeChassisAdmin(admin.ModelAdmin):
    pass


@admin.register(BladeServer)
class BladeServerAdmin(admin.ModelAdmin):
    pass


@admin.register(RackServer)
class RackServerAdmin(admin.ModelAdmin):
    pass


@admin.register(GeneralServer)
class GeneralServerAdmin(admin.ModelAdmin):
    pass


@admin.register(ServerModel)
class ServerModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ServerRole)
class ServerRoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    pass


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    pass