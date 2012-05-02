from django.contrib import admin

from onlyinpgh.accounts.models import UserProfile, BetaMember

admin.site.register(UserProfile)
admin.site.register(BetaMember)
