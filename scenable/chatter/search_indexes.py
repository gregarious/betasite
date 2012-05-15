from haystack import indexes
from scenable.chatter.models import Post


class PostTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Post
