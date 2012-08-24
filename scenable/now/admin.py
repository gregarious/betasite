from django.contrib import admin
from .models import FeaturedImage, Notice
from sorl.thumbnail.admin import AdminImageMixin


class FeaturedImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id', 'caption', 'dtcreated')


class NoticeAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'content')

admin.site.register(FeaturedImage, FeaturedImageAdmin)
admin.site.register(Notice, NoticeAdmin)
