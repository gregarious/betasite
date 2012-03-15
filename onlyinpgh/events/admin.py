from django.contrib import admin
from onlyinpgh.events.models import Event, Role, EventMeta


class RoleInline(admin.TabularInline):
    model = Role
    extra = 1
    radio_fields = {'role_type': admin.VERTICAL}


class MetaInline(admin.TabularInline):
    model = EventMeta
    extra = 1


class EventAdmin(admin.ModelAdmin):
    inlines = [RoleInline, MetaInline]
    list_display = ('name', 'place', 'dtstart', 'dtend')
    search_fields = ['name']
    ordering = ['dtstart']

admin.site.register(Event,EventAdmin)
