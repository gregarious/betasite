from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from scenable.common.views import PageContext

from scenable.now.viewmodels import NowFeedItem

from scenable.places.models import Place
from scenable.events.models import Event
from scenable.specials.models import Special
from scenable.chatter.models import Post
from scenable.news.models import Article

import random


### URL-LINKED VIEWS ###

def page_now(request):
    places = list(Place.listed_objects.all())
    random.shuffle(places)
    eligible_places = sorted(places, key=lambda p: -p.favorite_set.count())[:20]
    eligible_events = Event.listed_objects.filter(dtend__gt=now())
    eligible_specials = Special.objects.filter(dexpires__gte=now().date())

    objects = []
    objects += random.sample(eligible_places, min(4, len(eligible_places)))
    objects += random.sample(eligible_events, min(4, len(eligible_events)))
    objects += random.sample(eligible_specials, min(4, len(eligible_specials)))
    random.shuffle(objects)

    items = [NowFeedItem(obj) for obj in objects]
    articles = Article.objects.order_by('-publication_date')
    posts = Post.objects.order_by('-dtcreated')

    content = dict(
        items=items,
        news_articles=articles,
        chatter_posts=posts)

    page_context = PageContext(request,
        current_section='now',
        page_title='Scenable | Oakland Home',
        content_dict=content)

    return render_to_response('now/page_now.html', context_instance=page_context)
