from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex

from scenable.chatter.models import Post


class PostTextOnlyIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author__username')

    def get_model(self):
        return Post
