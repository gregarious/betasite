from django.shortcuts import get_object_or_404, render_to_response
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

#from scenable.common.utils.jsontools import serialize_resources, jsonp_response, sanitize_json
from scenable.common.views import PageContext, PageFilteredFeed
from scenable.common.utils.jsontools import sanitize_json

from scenable.places.models import Place
# from scenable.places.resources import PlaceFeedResource
from scenable.places.viewmodels import PlaceData, PlaceRelatedFeeds

from haystack.forms import SearchForm
from haystack.views import SearchView
from haystack.query import SearchQuerySet

import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class PagePlacesFeed(SearchView):
    def __init__(self, *args, **kwargs):
        self.search_used = False
        super(PagePlacesFeed, self).__init__(
            template='places/page_feed.html',
            form_class=SearchForm,
            results_per_page=8,
            searchqueryset=SearchQuerySet().all().models(Place)
        )

    def get_results(self):
        """
        If a query exists, fetch results via the form. Otherwise Fetches the results via the form.

        Returns an empty list if there's no query to search with.
        """
        if self.query:
            self.search_used = True
            return self.form.search()
        else:
            self.search_used = False
            return Place.listed_objects.all()

    def build_page(self):
        """
        Paginates the results appropriately. Pages will contains an actual
        model object, despite ragardless of whether the results returned
        were model instances or search results.
        """
        if self.search_used:
            processed_results = [PlaceData(result.object) for result in self.results]
        else:
            processed_results = [PlaceData(result) for result in self.results]

        paginator = Paginator(processed_results, self.results_per_page)

        page_no = self.request.GET.get('p')
        try:
            page = paginator.page(page_no)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            # if page out of range, return last one
            page = paginator.page(paginator.num_pages)
        return page

    def create_response(self):
        page = self.build_page()

        content = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'items_json': sanitize_json(json.dumps([p.serialize() for p in page])),
        }

        context = PageContext(self.request,
            current_section='places',
            page_title='Scenable | Oakland Places')
        return render_to_response(self.template, content, context_instance=context)


# class PagePlacesFeed(PageFilteredFeed):
#     def __init__(self, *args, **kwargs):
#         super(PagePlacesFeed, self).__init__(
#             model_class=Place,
#             viewmodel_class=PlaceData,
#             template='places/page_feed.html',
#             form_class=SearchForm,
#             results_per_page=8,
#         )

#     def create_response(self):
#         (paginator, page) = self.build_page()

#         places = [PlaceData(result.object) for result in page.object_list]

#         context = {
#             'query': self.query,
#             'form': self.form,
#             'page': page,
#             'items_json': sanitize_json(json.dumps([p.serialize() for p in places])),
#         }

#     def get_page_context(self, content):
#         return PageContext(self.request,
#             current_section='places',
#             page_title='Scenable | Oakland Places',
#             content_dict=content)

#     def hacked_unfiltered(self):
#         '''
#         Temporary hack to get a list of unfiltered results. Will either be
#         self.model_class.objects.all() or
#         self.model_class.listed_objects.all().

#         Necessary because self.searchqueryset.all() seems to be buggy.
#         '''
#         places = [p for p in Place.listed_objects.all()]
#         return sorted(places, key=lambda p: -p.favorite_set.count())

#     def hacked_filtered(self):
#         return [result.object for result in self.form.search()]


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
