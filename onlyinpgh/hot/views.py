from onlyinpgh.common.core.rendering import render_safe
from onlyinpgh.common.views import render_main, page_response

from onlyinpgh.hot.viewmodels import HotFeedCollection

### URL-LINKED VIEWS ###
def page_hot(request):
    hot_feeds = HotFeedCollection(request.user)
    main_content = render_main(render_safe('hot.html', hot_feeds=hot_feeds))
    return page_response(main_content, request)
