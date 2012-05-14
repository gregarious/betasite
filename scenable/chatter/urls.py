from django.conf.urls import patterns, url

urlpatterns = patterns('scenable.chatter.views',
    url(r'^$', 'page_feed', name='chatter-feed'),
)
