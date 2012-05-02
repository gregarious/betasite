from django.shortcuts import get_object_or_404, render_to_response
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

#from onlyinpgh.common.utils.jsontools import serialize_resources, jsonp_response, sanitize_json
from onlyinpgh.common.views import PageContext, PageFilteredFeed

from onlyinpgh.places.models import Place
# from onlyinpgh.places.resources import PlaceFeedResource
from onlyinpgh.places.viewmodels import PlaceData, PlaceRelatedFeeds

from haystack.forms import SearchForm


class PagePlacesFeed(PageFilteredFeed):
    def __init__(self, *args, **kwargs):
        super(PagePlacesFeed, self).__init__(
            model_class=Place,
            viewmodel_class=PlaceData,
            template='places/page_feed.html',
            form_class=SearchForm,
            results_per_page=8,
        )

    def get_page_context(self, content):
        return PageContext(self.request,
            current_section='places',
            page_title='Scenable | Oakland Places',
            content_dict=content)

    def hacked_unfiltered(self):
        '''
        Temporary hack to get a list of unfiltered results. Will either be
        self.model_class.objects.all() or
        self.model_class.listed_objects.all().

        Necessary because self.searchqueryset.all() seems to be buggy.
        '''
        return Place.listed_objects.all()


@login_required
def page_details(request, pid):
    '''
    Returns page response with main content set as:
        place (PlaceContext object)
        related_feeds (PlaceRelatedFeeds object)
    '''
    # build and render place detail viewmodel
    place = get_object_or_404(Place, id=pid)
    details = PlaceData(place, user=request.user)

    # build related feeds viewmodel
    related_feeds = PlaceRelatedFeeds(place, user=request.user)

    content = dict(
        place=details,
        related_feeds=related_feeds)
    page_context = PageContext(request,
        current_section='places',
        page_title='Scenable | %s' % place.name,
        #meta_content=place.description
        content_dict=content)

    return render_to_response('places/page_place.html', context_instance=page_context)
