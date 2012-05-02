from django.conf.urls import patterns, url

urlpatterns = patterns('onlyinpgh.accounts.views',
    url(r'^(?P<uname>[\w.+-]+)/$', 'page_public_account', name='account-public'),
    url(r'^(?P<uname>[\w.+-]+)/manage/$', 'page_manage_account', name='account-manage'),
    url(r'^(?P<uname>[\w.+-]+)/places/$', 'page_user_favorites', name='account-places'),
    url(r'^(?P<uname>[\w.+-]+)/events/$', 'page_user_attendance', name='account-events'),
    url(r'^(?P<uname>[\w.+-]+)/specials/$', 'page_user_coupons', name='account-specials'),
)
