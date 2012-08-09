from tastypie.resources import ModelResource
from tastypie.constants import ALL

from scenable.news.models import Article

from django.template.defaultfilters import truncatewords


### API RESOURCES ###
class NewsResource(ModelResource):
    class Meta:
        queryset = Article.objects.all()
        filtering = {
            'publication_date': ALL,
        }
        excludes = ('related_places', 'related_events',)
        allowed_methods = ['get']

    def dehydrate_blurb(self, bundle):
        return truncatewords(bundle.obj.blurb, 60)
