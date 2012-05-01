from django.conf.urls import patterns, url
from onlyinpgh.places.views import PagePlacesFeed

from haystack.views import search_view_factory

urlpatterns = patterns('onlyinpgh.places.views',
    url(r'^$', search_view_factory(view_class=PagePlacesFeed), name='places-feed'),
    url(r'^(?P<pid>\d+)/$', 'page_details', name='place-detail'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)$', 'detail_app'),

    # url(r'^lookup/all$', 'place_lookup'),
)
