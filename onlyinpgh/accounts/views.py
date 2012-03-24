from django.http import HttpResponse
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from onlyinpgh.outsourcing.apitools import facebook
from django.utils import safestring
import json


def home(request):
    abs_channel_uri = request.build_absolute_uri(
        reverse('onlyinpgh.accounts.views.channel_file'))
    fb_reg_uri = request.build_absolute_uri(
        reverse('onlyinpgh.accounts.views.fb_registration_handler'))
    return render_to_response('accounts/home_test.html',
        {'app_id': facebook.SCENABLE_APP_ID,
         'channel_uri': abs_channel_uri,
         'fb_registration_handler_uri': fb_reg_uri})


def fb_registration_handler(request):
    s = 'POST:<br/>'
    s += str(request.POST)
    s += '<br/>GET:'
    s += str(request.GET)
    s += '<br/>request:'
    s += str(request)
    return HttpResponse(safestring.mark_safe(s))


def channel_file(request):
    response = HttpResponse('<script src="//connect.facebook.net/en_US/all.js"></script>')
    year_secs = 60 * 60 * 24 * 365
    year_delta = timedelta(seconds=year_secs)
    response['Pragma'] = 'public'
    response['Cache-Control'] = 'max-age=%d' % year_secs
    response['Expires'] = (datetime.utcnow() + year_delta).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response
