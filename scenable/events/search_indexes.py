from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex

from scenable.events.models import Event

class EventTextOnlyIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    dtstart = indexes.DateTimeField(model_attr='dtstart')
    dtend = indexes.DateTimeField(model_attr='dtend')
    allday = indexes.BooleanField(model_attr='allday')
    listed = indexes.BooleanField(model_attr='listed')

    # FUTURE: Add categories for filtering directly in the SearchQuerySet

    def should_update(self, instance, **kwargs):
        return instance.listed

    def get_model(self):
        return Event

    def get_updated_field(self):
        return 'dtmodified'
