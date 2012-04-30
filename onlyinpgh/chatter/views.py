from django.shortcuts import render_to_response
from onlyinpgh.common.views import PageContext
from onlyinpgh.chatter.models import Post


def page_feed(request):
    items = Post.objects.all().order_by('-dtcreated')
    context = PageContext(request,
        current_section='chatter',
        page_title='Scenable | Chatter Feed',
        content_dict={'items': items})
    return render_to_response('chatter/page_feed.html', context_instance=context)
