from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.specials.views',
    url(r'^$', 'feed_page'),
    url(r'^feed/$', 'feed_page'),
    url(r'^(?P<oid>\d+)/$', 'detail_page', name='specials-item-detail'),

    url(r'^app/feed/$', 'feed_app'),
    url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
