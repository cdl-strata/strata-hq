from django.contrib import admin

from .models import Team, Site

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    pass