from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.views.generic.simple import redirect_to, direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from haystack.forms import SearchForm
from haystack.views import search_view_factory
from scenable.common.views import PageSiteSearch
from scenable import settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'scenable.common.views.page_home', name='home'),

    url(r'^login/$', 'scenable.accounts.views.page_login', name='login'),
    url(r'^signup/$', 'scenable.accounts.views.page_signup', name='signup'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/login/'}),

    url(r'^accounts/', include('scenable.accounts.urls')),

    url(r'^djadmin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^/prelaunchadmin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^oakland/$', 'scenable.common.views.page_beta_home', name='beta-home'),
    url(r'^oakland/places/', include('scenable.places.urls')),
    url(r'^oakland/events/', include('scenable.events.urls')),
    url(r'^oakland/specials/', include('scenable.specials.urls')),
    url(r'^oakland/news/', include('scenable.news.urls')),
    url(r'^oakland/chatter/', include('scenable.chatter.urls')),
    url(r'^oakland/now/$', 'scenable.now.views.page_now', name='now'),

    url(r'^oakland/tags/', include('scenable.tags.urls')),

    url(r'^manage/', include('scenable.orgadmin.urls')),

    # QR-code redirect handling
    url(r'^qr/$', 'scenable.common.views.qr_redirect'),
    url(r'^qr$', 'scenable.common.views.qr_redirect'),
    url(r'^qr/(\w+)/$', 'scenable.common.views.qr_redirect'),
    url(r'^qr/(\w+)$', 'scenable.common.views.qr_redirect'),

    # feedback form
    url(r'^feedback/ajax/generic/$', 'scenable.feedback.ajax.submit_generic'),

    # Scenable and Oakland shirt QRs
    url(r'^mobile-about/$', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url(r'^oakland-teaser/$', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    # Error pages
    url(r'^500.html$', direct_to_template, {'template': '500.html'}, name='500'),
    url(r'^404.html$', direct_to_template, {'template': '404.html'}, name='404'),
    url(r'^403.html$', direct_to_template, {'template': '403.html'}, name='403'),
    url(r'^index.html$', direct_to_template, {'template': 'index.html'}, name='index'),

    # Static about page for the scenable.com. TODO: organize the about pages
    url(r'^about/$', direct_to_template, {'template': 'qr/about.html'}, name='about'),

    url(r'^oakland/search/', search_view_factory(
        view_class=PageSiteSearch,
        template='search/page_site_search.html',
        form_class=SearchForm
    ), name='site-search'),

    # Static pages
    url(r'^about-oakland/$', 'scenable.common.views.page_static_about_oakland', name='about-oakland'),
    url(r'^team/$', 'scenable.common.views.page_static_team', name='team'),
    url(r'^mission/$', 'scenable.common.views.page_static_mission', name='mission'),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
