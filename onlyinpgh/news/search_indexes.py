from haystack import indexes
from onlyinpgh.news.models import Article


class ArticleTextOnlyIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Article
