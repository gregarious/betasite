from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.specials.views',
    url(r'^$', 'page_feed', name='specials-feed'),
    url(r'^feed/$', 'page_feed'),
    url(r'^(?P<sid>\d+)/$', 'page_details', name='special-detail'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
