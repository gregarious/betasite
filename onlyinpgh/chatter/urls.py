from django.conf.urls import patterns, url

urlpatterns = patterns('onlyinpgh.chatter.views',
    url(r'^$', 'page_feed', name='chatter-feed'),
)
