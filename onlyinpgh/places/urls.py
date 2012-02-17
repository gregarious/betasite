from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('places.views',
    url(r'^$', 'feed_page'),
    url(r'^feed/$', 'feed_page'),
    url(r'^detail/(?P<pid>\d+)/$', 'detail_page'),

    url(r'^app/feed/$', 'feed_app'),
    url(r'^app/detail/(?P<pid>\d+)/$', 'detail_app'),
)