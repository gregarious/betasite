from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'http://scenable.com/blog/'}),

    url(r'^fbtests/$', 'onlyinpgh.accounts.views.home'),
    url(r'^fbtests/fbreg/$', 'onlyinpgh.accounts.views.fb_registration_handler', name='fb_registration_handler'),
    url(r'^fbtests/channel.html$', 'onlyinpgh.accounts.views.channel_file'),
)