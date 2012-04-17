from onlyinpgh.common.views import render_page
from onlyinpgh.common.contexts import PageContext

from onlyinpgh.hot.contexts import HotFeedCollection


### URL-LINKED VIEWS ###
def page_hot(request):
    hot_feeds = HotFeedCollection(request.user)

    page_context = PageContext(request, 'hot', dict(
        hot_feeds=hot_feeds))
    return render_page('page_hot.html', page_context)
