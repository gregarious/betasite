from django.contrib import admin
from onlyinpgh.places.models import Place, Location, PlaceMeta


class PlaceMetaInline(admin.TabularInline):
    model = PlaceMeta
    extra = 1


class PlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceMetaInline]


class LocationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Place, PlaceAdmin)
admin.site.register(Location)
