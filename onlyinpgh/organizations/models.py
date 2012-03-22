from django.db import models
from django.contrib.auth.models import User
from onlyinpgh.places.models import Place


class Organization(models.Model):
    '''
    Represents organizations in the community (business, charity, etc.)
    '''
    name = models.CharField(max_length=200)

    administrators = models.ManyToManyField(User, blank=True, null=True)
    establishments = models.ManyToManyField(Place, blank=True, null=True)

    image_url = models.URLField(max_length=400, blank=True)
    url = models.URLField(blank=True)
    fb_id = models.CharField(max_length=50, blank=True)
    twitter_username = models.CharField(max_length=15, blank=True)

    def __unicode__(self):
        return self.name
