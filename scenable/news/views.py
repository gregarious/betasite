from django.shortcuts import render_to_response
from scenable.common.views import PageContext
from scenable.news.models import Article
from django.contrib.auth.decorators import login_required


##@login_required
def page_feed(request):
    items = Article.objects.order_by('-publication_date', '-dtcreated')
    context = PageContext(request,
        current_section='news',
        page_title='Scenable | News Feed',
        content_dict={'items': items})
    return render_to_response('news/page_feed.html', context_instance=context)
