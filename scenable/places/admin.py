from django.contrib import admin
from scenable.places.models import Place, Location, PlaceMeta, Category


class PlaceMetaInline(admin.TabularInline):
    model = PlaceMeta
    extra = 1


class PlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceMetaInline]
    list_display = ('name', 'dtcreated', 'id')
    exclude = ('hours',)


class LocationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Place, PlaceAdmin)
admin.site.register(Location)
admin.site.register(Category)
