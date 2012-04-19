from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.accounts.views',
    url(r'^manage/$', 'page_manage_account', name='account-manage'),
    url(r'^places/$', 'page_user_favorites', name='account-places'),
    url(r'^events/$', 'page_user_attendance', name='account-events'),
    url(r'^specials/$', 'page_user_coupons', name='account-specials'),

    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)
