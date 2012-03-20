from django.db import models

from django.contrib.auth.models import User

from onlyinpgh.places.models import Place
from onlyinpgh.tags.models import Tag
from onlyinpgh.organizations.models import Organization


class Event(models.Model):
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

    tags = models.ManyToManyField(Tag, blank=True)
    invisible = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


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
        ('organizer', 'Organizer'),
        ('referer', 'Referer'),
    )
    event = models.ForeignKey(Event)
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES)
    organization = models.ForeignKey(Organization)


class Attendee(models.Model):
    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)

    def __unicode__(self):
        return unicode(self.user) + u'@' + unicode(self.event)
