from django.contrib import admin
from scenable.feedback.models import GenericFeedbackComment


class GenericCommentAdmin(admin.ModelAdmin):
    list_display = ('feedback', 'user',)

admin.site.register(GenericFeedbackComment, GenericCommentAdmin)
