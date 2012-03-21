from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.events.views',
    url(r'^$', 'feed_page'),
    url(r'^feed/$', 'feed_page'),
    url(r'^(?P<eid>\d+)/$', 'detail_page', name='events-item-detail'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
