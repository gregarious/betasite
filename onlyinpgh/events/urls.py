from django.conf.urls import patterns, url
from onlyinpgh.events.views import PageEventsFeed

from haystack.views import search_view_factory

urlpatterns = patterns('onlyinpgh.events.views',
    url(r'^$', search_view_factory(view_class=PageEventsFeed), name='events-feed'),
    url(r'^(?P<eid>\d+)/$', 'page_details', name='event-detail'),
)

urlpatterns += patterns('onlyinpgh.events.ajax',
    url(r'^ajax/attend/$', 'event_attend'),
)
