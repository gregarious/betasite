from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('onlyinpgh.places.views',
    url(r'^$', 'feed_page'),
    url(r'^feed/$', 'feed_page'),
    url(r'^(?P<pid>\d+)/$', 'detail_page', name='places-item-detail'),

    url(r'^app/feed/$', 'feed_app'),
    url(r'^app/(?P<pid>\d+)$', 'detail_app'),
)
