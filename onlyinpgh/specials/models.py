from django.db import models

from onlyinpgh.common.core.viewmodels import ViewModel

from onlyinpgh.places.models import Place
from onlyinpgh.tags.models import Tag


class Special(models.Model, ViewModel):
    class Meta:
        ordering = ['title']

    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    points = models.IntegerField()
    place = models.ForeignKey(Place)

    dtexpires = models.DateTimeField(null=True, blank=True)
    dtstart = models.DateTimeField(null=True, blank=True)

    total_available = models.IntegerField(null=True, blank=True)
    total_sold = models.IntegerField(default=0)

    tags = models.ManyToManyField(Tag, blank=True)

    def to_data(self):
        '''
        Manually handle place and tag entries.
        '''
        data = super(Special, self).to_data()
        data.pop('place_id')
        data['place'] = self.place.to_data()
        data['tags'] = [t.to_data() for t in self.tags.all()]
        return data

    def __unicode__(self):
        return self.title

class SpecialMeta(models.Model):
    special = models.ForeignKey(Special)
    key = models.CharField(max_length=32)
    value = models.TextField()

    def __unicode__(self):
        val = self.value if len(self.value) < 20 \
                else self.value[:16] + '...'
        return u'%s: %s' % (self.key, val)
