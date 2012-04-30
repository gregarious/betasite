from django.shortcuts import render_to_response
from onlyinpgh.common.views import PageContext

from onlyinpgh.now.viewmodels import NowFeedItem

from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.specials.models import Special
import random


### URL-LINKED VIEWS ###
def page_now(request):
    # TODO: logic to pick relevant items
    objects = []
    objects += random.sample(Place.objects.all(), min(4, Place.objects.count()))
    objects += random.sample(Event.objects.all(), min(4, Event.objects.count()))
    objects += random.sample(Special.objects.all(), min(4, Special.objects.count()))
    random.shuffle(objects)

    items = [NowFeedItem(obj) for obj in objects]

    content = {'items': items}

    page_context = PageContext(request,
        current_section='now',
        page_title='Scenable | Oakland Places',
        content_dict=content)

    return render_to_response('now/page_now.html', context_instance=page_context)
