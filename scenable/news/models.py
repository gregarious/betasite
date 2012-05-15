from django.db import models

from scenable.places.models import Place
from scenable.events.models import Event


class Article(models.Model):
    class Meta:
        ordering = ['title']
    dtcreated = models.DateTimeField(auto_now_add=True)

    title = models.CharField(max_length=80)
    blurb = models.TextField(help_text=u'Short excerpt/description of the article (max 350 characters)', max_length=350)
    publication_date = models.DateField(help_text=u'Date source article published')

    fulltext_url = models.URLField(help_text=u'Link to the full article', max_length=400)
    source_name = models.CharField(max_length=100)
    source_site = models.URLField(help_text=u'Link to source\'s website', max_length=400, blank=True)
    image_url = models.URLField(max_length=400)

    related_places = models.ManyToManyField(Place, help_text=u'Places related to this article', null=True, blank=True)
    related_events = models.ManyToManyField(Event, help_text=u'Events related to this article', null=True, blank=True)

    def __unicode__(self):
        return self.title
