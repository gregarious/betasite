from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex

from scenable.specials.models import Special


class SpecialTextOnlyIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    dexpires = indexes.DateTimeField(model_attr='dexpires', null=True)
    dstart = indexes.DateTimeField(model_attr='dstart', null=True)

    def get_model(self):
        return Special

    def get_updated_field(self):
        return 'dtmodified'
