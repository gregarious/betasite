from django.db import models
from django.contrib.contenttypes import generic

from onlyinpgh.places.models import Place
from onlyinpgh.tags.models import Tag

class Offer(models.Model):
    description = models.TextField()
    point_value = models.PositiveIntegerField()
    place = models.ForeignKey(Place)
    tags = models.ManyToManyField(Tag,blank=True)
