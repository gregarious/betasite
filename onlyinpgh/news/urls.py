from django.conf.urls import patterns, url

urlpatterns = patterns('onlyinpgh.news.views',
    url(r'^$', 'page_feed', name='news-feed'),
)
