from django.db import models

from django.contrib.auth.models import User
from django.template.defaultfilters import truncatechars


class Post(models.Model):
    dtcreated = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=140)
    author = models.ForeignKey(User)

    def __unicode__(self):
        return '"%s" by %s' % (truncatechars(self.content, 15), self.author.username)
