from django.conf.urls import patterns, url

urlpatterns = patterns('scenable.orgadmin.views',
    url(r'^$', 'page_index'),
    url(r'^home/$', 'page_home', name='orgadmin-home'),

    url(r'^linkorg/$', 'page_link_org', name='orgadmin-linkorg'),

    url(r'^signup/$', 'page_signup', name='orgadmin-signup'),
    url(r'^login/$', 'page_login', name='orgadmin-login'),
    url(r'^logout/$', 'page_logout', name='orgadmin-logout'),

    # handle new place creations, and place claiming with page_setup_place_wizard
    url(r'^places/setup/claim/$', 'page_claim_place', name='orgadmin-claimplace'),
    url(r'^places/setup/new/$', 'page_edit_place', name='orgadmin-addplace'),

    url(r'^places/edit/(?P<id>\d+)/$', 'page_edit_place', name='orgadmin-editplace'),
    url(r'^places/remove/(?P<id>\d+)/$', 'page_remove_place', name='orgadmin-delplace'),
    url(r'^places/list/$', 'page_list_places', name='orgadmin-listplaces'),

    url(r'^events/edit/new/$', 'page_edit_event', name='orgadmin-addevent'),
    url(r'^events/edit/(?P<id>\d+)/$', 'page_edit_event', name='orgadmin-editevent'),
    url(r'^places/delete/(?P<id>\d+)/$', 'page_delete_event', name='orgadmin-delevent'),
    url(r'^events/list/$', 'page_list_events', name='orgadmin-listevents'),

    url(r'^specials/edit/new/$', 'page_edit_special', name='orgadmin-addspecial'),
    url(r'^specials/edit/(?P<id>\d+)/$', 'page_edit_special', name='orgadmin-editspecial'),
    url(r'^specials/delete/(?P<id>\d+)/$', 'page_delete_special', name='orgadmin-delspecial'),
    url(r'^specials/list/$', 'page_list_specials', name='orgadmin-listspecials'),
)

urlpatterns += patterns('scenable.orgadmin.ajax',
    url(r'^ajax/placeclaim_ac/$', 'place_claim_autocomplete'),
    url(r'^ajax/place_ac/$', 'place_autocomplete'),

    url(r'^ajax/place_confirm/$', 'place_confirm_div'),

    url(r'^ajax/newplace_submit/$', 'newplace_form_submission', name='orgadmin-ajax-newplace'),
)
