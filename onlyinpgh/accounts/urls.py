from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.accounts.views',
    url(r'^profile/$', 'page_profile'),
    url(r'^places/$', 'page_my_places'),
    url(r'^events/$', 'page_my_events'),
    url(r'^specials/$', 'page_my_specials'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
