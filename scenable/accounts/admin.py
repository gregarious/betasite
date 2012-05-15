from django.contrib import admin

from scenable.accounts.models import UserProfile, BetaMember

admin.site.register(UserProfile)
admin.site.register(BetaMember)
