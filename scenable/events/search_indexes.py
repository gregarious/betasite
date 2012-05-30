from haystack import indexes
from scenable.events.models import Event


class EventTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    dtstart = indexes.DateTimeField(model_attr='dtstart')
    dtend = indexes.DateTimeField(model_attr='dtend')
    allday = indexes.BooleanField(model_attr='allday')
    listed = indexes.BooleanField(model_attr='listed')

    def should_update(self, instance, **kwargs):
        return instance.listed

    def get_model(self):
        return Event
