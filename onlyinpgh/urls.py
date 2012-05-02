from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template

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
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs={'next_page': '/login/'}),

    url(r'^accounts/', include('onlyinpgh.accounts.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^manage/', include('onlyinpgh.orgadmin.urls')),

    url(r'^now/$', 'onlyinpgh.now.views.page_now', name='now'),

    url(r'^places/', include('onlyinpgh.places.urls')),
    url(r'^events/', include('onlyinpgh.events.urls')),
    url(r'^specials/', include('onlyinpgh.specials.urls')),
    url(r'^news/', include('onlyinpgh.news.urls')),
    url(r'^chatter/', include('onlyinpgh.chatter.urls')),

    url(r'^tags/', include('onlyinpgh.tags.urls')),

    # QR-code redirect handling
    url(r'^qr/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)/$', 'onlyinpgh.common.views.qr_redirect'),
    url(r'^qr/(\w+)$', 'onlyinpgh.common.views.qr_redirect'),

    # Scenable and Oakland shirt QRs
    url(r'^mobile-about/$', direct_to_template, {'template': 'qr/mobile_about.html'}, name='mobile-about'),
    url(r'^oakland-teaser/$', direct_to_template, {'template': 'qr/oakland_teaser.html'}, name='oakland-teaser'),

    # Error pages
    url(r'^500/$', direct_to_template, {'template': '500.html'}, name='500'),
    url(r'^404/$', direct_to_template, {'template': '404.html'}, name='404'),
    url(r'^403/$', direct_to_template, {'template': '403.html'}, name='403'),

    # Static about page for the scenable.com. TODO: organize the about pages
    url(r'^about/$', direct_to_template, {'template': 'qr/about.html'}, name='about'),

    url(r'^search/', search_view_factory(
        view_class=PageSiteSearch,
        template='search/page_site_search.html',
        form_class=SearchForm
    ), name='site-search'),

    # Staic pages
    url(r'^about-oakland/$', 'onlyinpgh.common.views.page_static_about_oakland', name='about-oakland'),
    url(r'^team/$', 'onlyinpgh.common.views.page_static_team', name='team'),
    url(r'^mission/$', 'onlyinpgh.common.views.page_static_mission', name='mission'),
)

# Tastypie API setup
# # disabled for the time being
# from tastypie.api import Api
# from onlyinpgh.places.resources import PlaceFeedResource
# v1_api = Api(api_name='v1')
# v1_api.register(PlaceFeedResource())

# urlpatterns += patterns('',
#     url(r'^api/', include(v1_api.urls)),
# )


from onlyinpgh import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
