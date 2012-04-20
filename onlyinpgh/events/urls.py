from django.conf.urls import patterns, url

urlpatterns = patterns('onlyinpgh.events.views',
    url(r'^$', 'page_feed', name='events-feed'),
    url(r'^feed/$', 'page_feed'),
    url(r'^(?P<eid>\d+)/$', 'page_details', name='event-detail'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
