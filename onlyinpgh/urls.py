from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from haystack.forms import SearchForm
from haystack.views import search_view_factory
from onlyinpgh.common.views import PageSiteSearch
from onlyinpgh import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'http://scenable.com/blog/'}),

    url(r'^fbtests/$', 'onlyinpgh.accounts.views.home'),
    url(r'^fbtests/fbreg/$', 'onlyinpgh.accounts.views.fb_registration_handler', name='fb_registration_handler'),
    url(r'^fbtests/channel.html$', 'onlyinpgh.accounts.views.channel_file'),
)
