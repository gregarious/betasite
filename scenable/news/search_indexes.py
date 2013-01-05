from haystack import indexes
from celery_haystack.indexes import CelerySearchIndex
from scenable.news.models import Article


class ArticleTextOnlyIndex(CelerySearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    publication_date = indexes.DateField(model_attr='publication_date')
    source_name = indexes.CharField(model_attr='source_name')

    def get_model(self):
        return Article

    def get_updated_field(self):
        return 'dtmodified'
