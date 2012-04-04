from django.db import models

from django.contrib.auth.models import User

from onlyinpgh.common.core.viewmodels import ViewModel
from onlyinpgh.places.models import Place
from onlyinpgh.tags.models import Tag
from onlyinpgh.organizations.models import Organization


class ListedEventManager(models.Manager):
    def get_query_set(self):
        return super(ListedEventManager, self).get_query_set().filter(listed=True)


class Event(models.Model, ViewModel):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    dtcreated = models.DateTimeField('created datetime', auto_now_add=True)
    dtmodified = models.DateTimeField('modified datetime', auto_now=True)

    dtstart = models.DateTimeField('start datetime')
    # dtend is the non-inclusive end date/time, meaning an event with dtend at 11pm actually only takes up time till 10:59pm
    # for all day events, this should be set to the next date (time irrelevant)
    # in a recurring event, dtend specifies FIRST occurrance end time, not end time of whole range
    dtend = models.DateTimeField('end datetime')
    allday = models.BooleanField('all day?', default=False)

    image_url = models.URLField(max_length=400, blank=True)

    url = models.URLField(blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    # simple plaintext field to be used as a fallback when only unlinkable, text-based place info is available (e.g. from an iCal feed)
    place_primitive = models.CharField(max_length=200, blank=True)

    tags = models.ManyToManyField(Tag, blank=True)
    listed = models.BooleanField(default=True)

    objects = models.Manager()
    listed_objects = ListedEventManager()

    def __unicode__(self):
        return self.name

    def to_data(self, *args, **kwargs):
        '''
        Manually handle place and tag entries.
        '''
        data = super(Event, self).to_data(*args, **kwargs)
        data.pop('place_id')
        data['place'] = self.place.to_data(*args, **kwargs) if self.place else None
        data['tags'] = [t.to_data(*args, **kwargs) for t in self.tags.all()]
        return data


class EventMeta(models.Model):
    event = models.ForeignKey(Event)
    key = models.CharField(max_length=32)
    value = models.TextField()

    def __unicode__(self):
        val = self.value if len(self.value) < 20 \
                else self.value[:16] + '...'
        return u'%s: %s' % (self.key, val)


class Role(models.Model):
    ROLE_TYPES = (
        ('owner', 'Owner'),
    )
    event = models.ForeignKey(Event)
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES)
    organization = models.ForeignKey(Organization)


class Attendee(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    dtcreated = models.DateTimeField('Time user added event', auto_now_add=True)

    dtmodified = models.DateTimeField('Time user changed attendance status', auto_now=True)
    # This flag must be True to consider user as attending
    # defaults to True, but can be False is user revokes attendance
    is_attending = models.BooleanField('Is user attending?"', default=True)

    def revoke_attendance(self):
        '''
        After using this function, Attendee should never be used again:
        create new one if user wants to re-attend.
        '''
        self.is_attending = False
        self.save()

    def __unicode__(self):
        return unicode(self.user) + u'@' + unicode(self.event)
