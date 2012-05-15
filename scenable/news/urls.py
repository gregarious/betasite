from django.conf.urls import patterns, url

urlpatterns = patterns('scenable.news.views',
    url(r'^$', 'page_feed', name='news-feed'),
)
