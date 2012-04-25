from django.shortcuts import render_to_response
from onlyinpgh.common.views import PageContext

from onlyinpgh.hot.viewmodels import HotFeedCollection


### URL-LINKED VIEWS ###
def page_hot(request):
    hot_feeds = HotFeedCollection(request.user)

    content = {'hot_feeds': hot_feeds}

    page_context = PageContext(request,
        current_section='hot',
        page_title='Scenable | Oakland Places',
        content_dict=content)

    return render_to_response('hot/page_hot.html', page_context)
