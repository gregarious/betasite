from django.db import models

from django.contrib.auth.models import User

from scenable.common.core.viewmodels import ViewModel
from scenable.places.models import Place
from scenable.tags.models import Tag
from scenable.accounts.models import Organization
from scenable.common.utils import precache_thumbnails


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

    image = models.ImageField(upload_to='img/e', null=True, blank=True)

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

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        if self.image:
            # pre-cache common sized thumbnails
            try:
                precache_thumbnails(self.image)
            # never let these lines interrupt anything
            except Exception as e:
                print 'error caching thumbnails', e
                # TODO: log error

    def to_data(self, *args, **kwargs):
        '''
        Manually handle place and tag entries.
        '''
        data = super(Event, self).to_data(*args, **kwargs)
        data.pop('place_id')
        data['place'] = self.place.to_data(*args, **kwargs) if self.place else None
        data['tags'] = [t.to_data(*args, **kwargs) for t in self.tags.all()]
        return data

    def add_attendee(self, user):
        '''
        Adds Attendee object to this Event's attendee_set.

        Returns True if new Attendee created, False if already existed
        '''
        _, created = self.attendee_set.get_or_create(user=user)
        return created

    def remove_attendee(self, user):
        '''
        Deletes Attendee object from this Event's attendee_set.

        Returns True if Attendee existed, False if it already didn't.
        '''
        attendees = self.attendee_set.filter(user=user)
        attendee_exists = attendees.count() != 0
        attendees.delete()
        return attendee_exists

    @models.permalink
    def get_absolute_url(self):
        return ('event-detail', (), {'eid': self.id})


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

    def __unicode__(self):
        return unicode(self.user) + u'@' + unicode(self.event)


class ICalendarFeed(models.Model):
    class Meta:
        verbose_name = 'iCalendar Feed'
    url = models.URLField(max_length=300)
    owner = models.ForeignKey(Organization, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    candidate_places = models.ManyToManyField(Place,
        verbose_name=u'A collection of Places that are likely venues for events in this feed',
        null=True, blank=True)

    def __unicode__(self):
        return self.name
