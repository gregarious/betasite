from django.conf.urls import patterns, url
from onlyinpgh.specials.views import PageSpecialsFeed

from haystack.views import search_view_factory

urlpatterns = patterns('onlyinpgh.specials.views',
    url(r'^$', search_view_factory(view_class=PageSpecialsFeed), name='specials-feed'),
    url(r'^(?P<sid>\d+)/$', 'page_details', name='special-detail'),

    url(r'^redeem/(?P<uuid>[\dA-Fa-f-]+)/$', 'page_coupon', name='specials-coupon'),
    # url(r'^app/feed/$', 'feed_app'),
    # url(r'^app/(?P<pid>\d+)/$', 'detail_app'),
)

urlpatterns += patterns('onlyinpgh.specials.ajax',
    url(r'^ajax/buy/$', 'coupon_buy'),
)
