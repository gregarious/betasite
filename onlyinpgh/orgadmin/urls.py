from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('onlyinpgh.orgadmin.views',
    url(r'^$', 'page_home'),
    url(r'^home/$', 'page_home', name='orgadmin-home'),

    url(r'^signup/$', 'page_signup'),
    url(r'^login/$', 'page_login', name='orgadmin-login'),
    url(r'^logout/$', 'page_logout'),

    # handle new place creations, and place claiming with page_setup_place_wizard
    url(r'^places/setup/claim/$', 'page_claim_place'),
    url(r'^places/setup/new/$', 'page_setup_place_wizard', name='orgadmin-addplace'),
    url(r'^places/setup/(?P<id>\d+)/$', 'page_setup_place_wizard'),

    url(r'^places/edit/(?P<id>\d+)/$', 'page_edit_place'),
    url(r'^places/remove/(?P<id>\d+)/$', 'page_remove_place'),
    url(r'^places/list/$', 'page_list_places'),

    url(r'^events/edit/new/$', 'page_edit_event', name='orgadmin-addevent'),
    url(r'^events/edit/(?P<id>\d+)/$', 'page_edit_event'),
    url(r'^places/delete/(?P<id>\d+)/$', 'page_delete_event'),
    url(r'^events/list/$', 'page_list_events'),

    url(r'^specials/edit/new/$', 'page_edit_special', name='orgadmin-addspecial'),
    url(r'^specials/edit/(?P<id>\d+)/$', 'page_edit_special'),
    url(r'^specials/delete/(?P<id>\d+)/$', 'page_delete_special'),
    url(r'^specials/list/$', 'page_list_specials'),
)
