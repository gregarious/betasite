from django.conf.urls import patterns, url

urlpatterns = patterns('onlyinpgh.accounts.views',
    url(r'^profile/$', 'page_profile', name='my-profile'),
    url(r'^places/$', 'page_my_places', name='my-places'),
    url(r'^events/$', 'page_my_events', name='my-events'),
    url(r'^specials/$', 'page_my_specials', name='my-specials'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
