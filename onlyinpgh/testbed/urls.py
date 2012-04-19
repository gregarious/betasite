from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('onlyinpgh.testbed.views',
    url(r'^$', 'home', name='testbed-home'),
)