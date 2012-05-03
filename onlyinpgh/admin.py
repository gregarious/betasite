from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

UserAdmin.list_display = ('username', 'email', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
