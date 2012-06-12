from django.contrib import admin

from scenable.accounts.models import UserProfile, BetaMember, Organization

admin.site.register(UserProfile)
admin.site.register(BetaMember)
admin.site.register(Organization)
