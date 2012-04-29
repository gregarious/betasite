from django.shortcuts import render_to_response
from onlyinpgh.common.views import PageContext
from onlyinpgh.news.models import Article


def page_feed(request):
    items = Article.objects.all()
    context = PageContext(request,
        current_section='news',
        page_title='Scenable | News Feed',
        content_dict={'items': items})
    return render_to_response('news/page_feed.html', context_instance=context)
