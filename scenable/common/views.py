from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse

from django.http import Http404
from django.template import RequestContext
from django.utils import timezone
from django.core.paginator import Paginator, InvalidPage

from haystack.views import SearchView
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from scenable.common.utils.jsontools import sanitize_json

import json


class PageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_section=None, page_title=None, content_dict={}, **kwargs):
        '''
        current_section: string among 'places', 'events', 'news', etc...
        content_dict: context variables for main_context
        '''
        page_title = "Scenable"

        variables = dict(
            page_title=page_title,
            current_section=current_section,
        )
        variables.update(content_dict)
        super(PageContext, self).__init__(request, variables, **kwargs)


def qr_redirect(request, key=None):
    if key is None:
        key = request.GET.get('id')

    if key == 'oakland':
        return redirect('oakland-teaser')
    elif key == 'shirt':
        return redirect('about')
    elif key == 'card':
        return redirect('about')
    elif key == 'poster':
        return redirect('oakland-teaser')
    elif key == 'halfsheet':
        return redirect('oakland-teaser')
    else:
        print 'not found', key
        raise Http404


class PageSiteSearch(SearchView):
    '''
    Class-based view inheriting from Haystack's basic SearchView.
    '''
    def create_response(self):
        '''
        Custom overwritten method to return a response with search results
        organized by type.

        Don't need pagination but do need to process the results in a custom
        manner, so create_response from SearchView is being completely
        overwritten.
        '''
        content = {
            'query': self.query,
            'form': self.form,
            'suggestion': None,
        }

        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            content['suggestion'] = self.form.get_suggestion()

        # organize the results by model type
        result_by_type = {}
        for r in self.results:
            thistype = result_by_type.setdefault(r.content_type(), [])
            thistype.append(r)

        # A couple of notes on Haystack:
        # - Can't use SearchQuerySet.filter for a cross-model search unless
        #   the same field is defined on each one. Search will just omit
        #   all results without the defined field if you try.
        # - As a result, using load_all=True (the default for SearchView
        #   forms), and filtering the objects manually.
        now, now_date = timezone.now(), timezone.now().date
        content['results'] = dict(
            places=result_by_type.get('places.place', []),
            events=[result for result in result_by_type.get('events.event', [])
                        if result.object.dtend > now],
            specials=[result for result in result_by_type.get('specials.special', [])
                        if result.object.dexpires is None or result.dexpires > now_date],
            news_articles=result_by_type.get('news.article', []),
            chatter_posts=result_by_type.get('chatter.post', []),
        )

        # doesn't do anything now, but copying it over from the overridden base method
        content.update(self.extra_context())

        context = PageContext(self.request,
            page_title="Scenable | Oakland Search",
            content_dict=content)
        return render_to_response(self.template, context_instance=context)


class FeedView(object):
    '''
    Class-based view that draws inspiration from Haystack's SearchView. We
    want similar functionality, but the ability to skip the SearchQuerySet
    if no search query is requested. Rather than hack around SearchView with
    it's internal assumption of results as SearchQueryResults, this one was
    created from scratch instead.

    Main difference is the methods that should be overridden. The following
    methods should all be overridden, with the exception of
    `apply_category_filter`, which can be omitted if the feed's model type does
    not support categories.

    - build_search_form: must return a SearchForm subclass (this also
        provides the means to fetch results when a query is requested)
    - get_all_results: must return an iterable of model instances
    - apply_category_filter: if defined, should use the contents of
        self.category to filter the list of results (optional)

    Also, the constructor argument page_context_factory should be a callable
    which takes a Request variable as its only argument and returns a
    PageContext instance.
    '''
    def __init__(self, template, page_context_factory, viewmodel_class=None, results_per_page=20):
        self.template = template
        self.results_per_page = results_per_page
        self.page_context_factory = page_context_factory

        # TODO: remove this when Tastypie or to_json methods added
        self.viewmodel_class = viewmodel_class

        self.query, self.category = None, None

    def __call__(self, request):
        """
        Generates the actual response to the search.

        Relies on internal, overridable methods to construct the response.
        """
        self.request = request

        data = None
        if len(self.request.GET):
            data = self.request.GET

        self.form = self.build_search_form(data)

        if self.form.is_valid():
            self.query = self.form.cleaned_data.get('q')
            self.category = self.form.cleaned_data.get('category')

        if self.query:
            self.results = [result.object for result in self.form.search()]
        else:
            self.results = self.get_all_results()

        self.results = self.apply_category_filter(self.category, self.results)

        # TODO: remove this when Tastypie or to_json methods added
        if self.viewmodel_class:
            self.results = map(self.viewmodel_class, self.results)

        return self.create_response()

    def build_search_form(self, data):
        """
        Instantiates the form the class should be used to process the search
        query
        """
        return SearchForm(searchqueryset=SearchQuerySet())

    def get_all_results(self):
        """
        Fetches the unfiltered results.
        """
        return []

    def apply_category_filter(self, category_key, results):
        '''
        Looks for a value in category_key and filters results accordingly.

        Defaults to identity function.
        '''
        return results

    def build_page(self):
        """
        Paginates the results appropriately.

        In case someone does not want to use Django's built-in pagination, it
        should be a simple matter to override this method to do what they would
        like.
        """
        try:
            page_no = int(self.request.GET.get('page', 1))
        except (TypeError, ValueError):
            raise Http404("Not a valid number for page.")

        if page_no < 1:
            raise Http404("Pages should be 1 or greater.")

        start_offset = (page_no - 1) * self.results_per_page
        self.results[start_offset:start_offset + self.results_per_page]

        paginator = Paginator(self.results, self.results_per_page)

        try:
            page = paginator.page(page_no)
        except InvalidPage:
            raise Http404

        return (paginator, page)

    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        (paginator, page) = self.build_page()

        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'items_json': sanitize_json(json.dumps([p.serialize() for p in page])),
        }

        return render_to_response(self.template, context,
            context_instance=self.page_context_factory(self.request))


### URL-LINKED VIEWS ###
def page_oakland_home(request):
    return redirect(reverse('now'))


def page_home(request):
    '''
    For the moment, the index page redirects to the /info blog.
    '''
    if request.is_secure():
        scheme = "https"
    else:
        scheme = "http"
    info_url = "%s://%s/info/" % (scheme, request.get_host())
    return redirect(info_url)


### STATIC PAGES ###
def page_static_about_oakland(request):
    context = PageContext(request, page_title="Scenable | About Oakland")
    return render_to_response('static_pages/about_oakland.html', context_instance=context)


def page_static_download_app(request):
    context = PageContext(request, page_title="Scenable | About the App")
    return render_to_response('static_pages/download_app.html', context_instance=context)


def page_static_team(request):
    context = PageContext(request, page_title="Scenable | The Team")
    return render_to_response('static_pages/team.html', context_instance=context)


def page_static_mission(request):
    context = PageContext(request, page_title="Scenable | Our Mission")
    return render_to_response('static_pages/mission.html', context_instance=context)
