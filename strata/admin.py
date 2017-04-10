from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.conf.urls import url
from django.core.urlresolvers import reverse

# Register your models here.
from .models import Server, Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    pass

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('hostname',),
        }),
        ('WebLogic', {
            'fields': ('adminserver_port', 'adminserver_username', 'adminserver_password',),
        }),
        ('Customer Environments', {
            'fields': ('environment', 'customer', ),
        }),
    )
    filter_horizontal = ('customer',)

    list_display = ('hostname', 'environment', 'get_customers', 'weblogic_status', 'weblogic_actions',)
    list_filter = ('environment', 'customer', )

    def get_customers(self, obj):
        return mark_safe("<br/>".join([s.name for s in obj.customer.all()]))
    get_customers.short_description = "Customers"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<server_id>.+)/start/$',
                self.admin_site.admin_view(self.weblogic_start),
                name='weblogic-start',
            ),
            url(
                r'^(?P<server_id>.+)/stop/$',
                self.admin_site.admin_view(self.weblogic_stop),
                name='weblogic-stop',
            ),
        ]
        return custom_urls + urls

    def weblogic_status(self, obj):
        return True
    weblogic_status.boolean = True

    def weblogic_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Start</a>&nbsp;'
            '<a class="button" href="{}">Stop</a>',
            reverse('admin:weblogic-start', args=[obj.pk]),
            reverse('admin:weblogic-stop', args=[obj.pk]),
        )

    def weblogic_start(self, obj):
        pass

    def weblogic_stop(self, obj):
        pass