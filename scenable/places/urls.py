from django.conf.urls import patterns, url
from scenable.places.views import PagePlacesFeed

from haystack.views import search_view_factory

urlpatterns = patterns('scenable.places.views',
    url(r'^$', search_view_factory(view_class=PagePlacesFeed), name='places-feed'),
    url(r'^(?P<pid>\d+)/$', 'page_details', name='place-detail'),
)

urlpatterns += patterns('scenable.places.ajax',
    url(r'^ajax/favorite/$', 'place_favorite'),
)
