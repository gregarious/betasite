from django.contrib import admin
from onlyinpgh.feedback.models import GenericFeedbackComment


class GenericCommentAdmin(admin.ModelAdmin):
    list_display = ('feedback', 'user',)

admin.site.register(GenericFeedbackComment, GenericCommentAdmin)
