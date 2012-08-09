from tastypie.resources import ModelResource
from tastypie.constants import ALL

from scenable.news.models import Article


### API RESOURCES ###
class NewsResource(ModelResource):
    class Meta:
        queryset = Article.objects.all()
        filtering = {
            'publication_date': ALL,
        }
        excludes = ('related_places', 'related_events',)
        allowed_methods = ['get']
