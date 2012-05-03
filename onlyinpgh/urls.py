from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from haystack.forms import SearchForm
from haystack.views import search_view_factory
from onlyinpgh.common.views import PageSiteSearch

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'onlyinpgh.common.views.page_home', name='home'),

    url(r'^login/$', 'onlyinpgh.accounts.views.page_login', name='login'),
    url(r'^signup/$', 'onlyinpgh.accounts.views.page_signup', name='signup'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/prelaunch/login/'}),

    url(r'^accounts/', include('onlyinpgh.accounts.urls')),

    url(r'^/djadmin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^/prelaunchadmin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^oakland/$', 'onlyinpgh.common.views.page_home', name='oakland-home'),
    url(r'^oakland/places/', include('onlyinpgh.places.urls')),
    url(r'^oakland/events/', include('onlyinpgh.events.urls')),
    url(r'^oakland/specials/', include('onlyinpgh.specials.urls')),
    url(r'^oakland/news/', include('onlyinpgh.news.urls')),
    url(r'^oakland/chatter/', include('onlyinpgh.chatter.urls')),
    url(r'^oakland/now/$', 'onlyinpgh.now.views.page_now', name='now'),

    url(r'^oakland/tags/', include('onlyinpgh.tags.urls')),

    url(r'^manage/', include('onlyinpgh.orgadmin.urls')),

    # QR-code redirect handling
    url(r'^qr/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)$', 'onlyinpgh.common.views.qr_redirect'),

    # feedback form
    url(r'^feedback/ajax/generic/$', 'onlyinpgh.feedback.ajax.submit_generic'),

    # Scenable and Oakland shirt QRs
    url(r'^mobile-about/$', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url(r'^oakland-teaser/$', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    # Error pages
    url(r'^500.html$', direct_to_template, {'template': '500.html'}, name='500'),
    url(r'^404.html$', direct_to_template, {'template': '404.html'}, name='404'),
    url(r'^403.html$', direct_to_template, {'template': '403.html'}, name='403'),

    # Static about page for the scenable.com. TODO: organize the about pages
    url(r'^about/$', direct_to_template, {'template': 'qr/about.html'}, name='about'),

    url(r'^oakland/search/', search_view_factory(
        view_class=PageSiteSearch,
        template='search/page_site_search.html',
        form_class=SearchForm
    ), name='site-search'),

    # Static pages
    url(r'^about-oakland/$', 'onlyinpgh.common.views.page_static_about_oakland', name='about-oakland'),
    url(r'^team/$', 'onlyinpgh.common.views.page_static_team', name='team'),
    url(r'^mission/$', 'onlyinpgh.common.views.page_static_mission', name='mission'),
)
