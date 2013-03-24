from haystack import indexes
from scenable.chatter.models import Post


class PostTextOnlyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author__username')

    def get_model(self):
        return Post
