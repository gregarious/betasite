from django.conf.urls import patterns, include, url

urlpatterns = patterns('onlyinpgh.testbed.views',
    url(r'^$', 'home', name='testbed-home'),
    url(r'^maps$', 'maps'),
)