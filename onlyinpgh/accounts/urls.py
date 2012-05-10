from django.conf.urls import patterns, url

# account profile urls
urlpatterns = patterns('onlyinpgh.accounts.views',
    url(r'^(?P<uname>[\w.+-]+)/$', 'page_public_account', name='account-public'),
    url(r'^(?P<uname>[\w.+-]+)/manage/$', 'page_manage_account', name='account-manage'),
    url(r'^(?P<uname>[\w.+-]+)/places/$', 'page_user_favorites', name='account-places'),
    url(r'^(?P<uname>[\w.+-]+)/events/$', 'page_user_attendance', name='account-events'),
    url(r'^(?P<uname>[\w.+-]+)/specials/$', 'page_user_coupons', name='account-specials'),
)

# password resetting urls
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^password/reset/$', 'password_reset', name='accounts-password_reset'),
    url(r'^password/reset/request-sent/$', 'password_reset_done'),
    url(r'^password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'password_reset_confirm', name='accounts-password_reset_confirm'),
    url(r'^password/reset/complete/$', 'password_reset_complete'),
)
