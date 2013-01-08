from django.shortcuts import get_object_or_404, render_to_response

from scenable.common.views import PageContext, FeedView
from scenable.common.forms import CategorySearchForm

from scenable.places.models import Place, Category
from scenable.places.viewmodels import PlaceData, PlaceRelatedFeeds

from haystack.query import SearchQuerySet
from django.db.models import Count


class PagePlacesFeed(FeedView):
    '''
    Class-based view that shows main feed of places
    '''

    def __init__(self):
        # used to render the page with correctly configured PageContext
        context_factory = lambda request: \
            PageContext(request,
                current_section='places',
                page_title='Scenable | Oakland Places')

        # set static attributes of the view class here
        super(PagePlacesFeed, self).__init__(
            template='places/page_feed.html',
            page_context_factory=context_factory,
            viewmodel_class=PlaceData,
            results_per_page=8)

    def build_search_form(self, data=None):
        '''
        Returns a form for that will search all Places with a place category
        dropdown.
        '''
        category_choices = [(str(cat.id), cat.label)
            for cat in Category.objects.order_by('id')]
        category_choices.insert(0, ('0', 'All Places'))

        return CategorySearchForm(choices=category_choices,
            searchqueryset=SearchQuerySet().models(Place),
            data=data)

    def get_all_results(self):
        '''
        Returns all places, sorted by number of favorites each has.
        '''
        return Place.listed_objects \
                .annotate(total_favs=Count('favorite')) \
                .order_by('-total_favs')

    def apply_category_filter(self, category_key, results):
        '''
        Only include results with the given category_key.
        '''
        # Don't filter if no category, or if category is '0' (this key refers
        # to "All Results").
        if not category_key or category_key == '0':
            return results

        # otherwise, apply and include filter for results that have the category
        contains_category = lambda obj: category_key in [str(cat.id) for cat in obj.categories.all()]
        return [result for result in results if contains_category(result)]


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
