from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)

    url = models.URLField(blank=True)
    fb_id = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)
