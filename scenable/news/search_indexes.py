from haystack import indexes
from scenable.news.models import Article


class ArticleTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    publication_date = indexes.DateField(model_attr='publication_date')
    source_name = indexes.CharField(model_attr='source_name')

    def get_model(self):
        return Article
