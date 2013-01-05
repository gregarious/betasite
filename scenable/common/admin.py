# Place to unregister any third-party admin panels

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

UserAdmin.list_display = ('username', 'email', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)

# disable all of the Celery admin sections

from djcelery.models import (TaskState, WorkerState,
                 PeriodicTask, IntervalSchedule, CrontabSchedule)

admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
