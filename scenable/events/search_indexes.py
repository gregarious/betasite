from haystack import indexes
from scenable.events.models import Event


class EventTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Event