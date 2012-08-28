from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth.decorators import login_required

from scenable.common.views import PageContext, PageFilterableFeed

from scenable.places.models import Place, Category
from scenable.places.viewmodels import PlaceData, PlaceRelatedFeeds

from haystack.query import SearchQuerySet
from django.db.models import Count


class PagePlacesFeed(PageFilterableFeed):
    def __init__(self, *args, **kwargs):
        sqs = SearchQuerySet().models(Place)
        qs = Place.listed_objects.annotate(total_favs=Count('favorite')).order_by('-total_favs')
        categories = [(str(cat.id), cat.label) for cat in Category.objects.order_by('id')]
        categories.insert(0, ('0', 'All Places'))

        super(PagePlacesFeed, self).__init__(
            template='places/page_feed.html',
            searchqueryset=sqs,
            nosearch_queryset=qs,
            categories=categories,
            viewmodel_class=PlaceData,
            results_per_page=8,
        )

    def get_page_context(self, request):
        '''
        Return a dict of extra context variables. Override this.
        '''
        return PageContext(self.request,
            current_section='places',
            page_title='Scenable | Oakland Places')

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
