from django.contrib import admin
from .models import FeaturedImage, Notice
from sorl.thumbnail.admin import AdminImageMixin


class FeaturedImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id', 'caption', 'dtcreated')

admin.site.register(FeaturedImage, FeaturedImageAdmin)
admin.site.register(Notice)
