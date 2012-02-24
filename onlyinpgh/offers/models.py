from django.db import models
from django.contrib.contenttypes import generic

from onlyinpgh.identity.models import Organization
from onlyinpgh.tags.models import Tag

class Offer(models.Model):
    description = models.TextField()
    point_value = models.PositiveIntegerField()
    sponsor = models.ForeignKey(Organization)
    tags = models.ManyToManyField(Tag,blank=True)
