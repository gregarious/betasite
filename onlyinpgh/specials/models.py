from django.db import models

from onlyinpgh.common.core.viewmodels import ViewModel

from django.contrib.auth.models import User
from onlyinpgh.places.models import Place
from onlyinpgh.tags.models import Tag

from datetime import datetime


class Special(models.Model, ViewModel):
    class Meta:
        ordering = ['title']

    dtcreated = models.DateTimeField('created datetime', auto_now_add=True)

    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    points = models.IntegerField(blank=True, default=0)
    place = models.ForeignKey(Place)

    dexpires = models.DateField(null=True, blank=True)
    dstart = models.DateField(null=True, blank=True)

    total_available = models.IntegerField(null=True, blank=True)
    total_sold = models.IntegerField(default=0, editable=False)

    tags = models.ManyToManyField(Tag, blank=True)

    def to_data(self, *args, **kwargs):
        '''
        Manually handle place and tag entries.
        '''
        data = super(Special, self).to_data(*args, **kwargs)
        data.pop('place_id')
        data['place'] = self.place.to_data(*args, **kwargs)
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


class Coupon(models.Model):
    '''Coupon is a user-owned Special'''
    special = models.ForeignKey(Special)
    user = models.ForeignKey(User)
    dtcreated = models.DateTimeField('Time user bought special', auto_now_add=True)

    dtused = models.DateTimeField('Time user used special', default=None, null=True, blank=True)
    was_used = models.BooleanField('Has coupon been used?"', default=False)

    def mark_used(self):
        '''
        After using this function, Coupon should never be used again.
        '''
        self.was_used = True
        self.dtused = datetime.now()
        self.save()
