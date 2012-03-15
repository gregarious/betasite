from django.contrib import admin

from accounts.models import UserProfile, Organization

admin.site.register(UserProfile)
admin.site.register(Organization)
