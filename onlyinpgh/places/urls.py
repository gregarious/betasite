from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.places.views',
    url(r'^$', 'page_feed', name='places-feed'),
    url(r'^feed/$', 'page_feed'),
    url(r'^(?P<pid>\d+)/$', 'page_details', name='place-detail'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)$', 'detail_app'),

    # url(r'^lookup/all$', 'place_lookup'),
)
