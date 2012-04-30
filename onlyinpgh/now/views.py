from django.shortcuts import render_to_response
from onlyinpgh.common.views import PageContext

from onlyinpgh.now.viewmodels import NowFeedItem

from onlyinpgh.places.models import Place
from onlyinpgh.events.models import Event
from onlyinpgh.specials.models import Special
from onlyinpgh.chatter.models import Post
from onlyinpgh.news.models import Article

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
    articles = Article.objects.order_by('-publication_date')
    posts = Post.objects.order_by('-dtcreated')

    content = dict(
        items=items,
        news_articles=articles,
        chatter_posts=posts)

    page_context = PageContext(request,
        current_section='now',
        page_title='Scenable | Oakland Places',
        content_dict=content)

    return render_to_response('now/page_now.html', context_instance=page_context)
