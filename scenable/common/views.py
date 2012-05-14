from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse

from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils import timezone

from haystack.views import SearchView
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet

from scenable.feedback.forms import GenericFeedbackForm
from scenable.common.utils.jsontools import sanitize_json
import json
import urlparse


def to_login(request):
    '''
    Temporary measure to emulate how the login_required decorator redirects
    an unauthenticated user (needed for clas-based search views)
    '''
    path = request.build_absolute_uri()
    # If the login url is the same scheme and net location then just
    # use the path as the "next" url.
    login_scheme, login_netloc = urlparse.urlparse(reverse('login'))[:2]
    current_scheme, current_netloc = urlparse.urlparse(path)[:2]
    if ((not login_scheme or login_scheme == current_scheme) and
        (not login_netloc or login_netloc == current_netloc)):
        path = request.get_full_path()
    return redirect_to_login(path, reverse('login'), REDIRECT_FIELD_NAME)


class PageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_section=None, page_title=None, content_dict={}, **kwargs):
        '''
        current_section: string among 'places', 'events', 'news', etc...
        content_dict: context variables for main_context
        '''
        if page_title is None:
            page_title = "Scenable: You are a Beautiful Flower"

        variables = dict(
            page_title=page_title,
            current_section=current_section,
            site_search_form=SearchForm(),
            sidebar_feedback_form=GenericFeedbackForm(user=request.user),
        )
        variables.update(content_dict)
        super(PageContext, self).__init__(request, variables, **kwargs)


def qr_redirect(request, key=None):
    if key is None:
        key = request.GET.get('id')

    if key == 'oakland':
        return redirect('oakland-teaser')
    elif key == 'shirt':
        return redirect('mobile-about')
    elif key == 'card':
        return redirect('mobile-about')
    else:
        print 'not found', key
        raise Http404


class PageSiteSearch(SearchView):
    '''
    Class-based view inheriting from Haystack's basic SearchView. Note that
    if this class is used with the search_view_factory, the site.
    '''
    def create_response(self):
        '''
        Custom overwritten method to return a response with search results
        organized by type.
        '''
        content = {
            'query': self.query,
            'form': self.form,
            'suggestion': None,
        }
        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            content['suggestion'] = self.form.get_suggestion()
        elif self.results:
            result_by_type = {}
            for r in self.results:
                thistype = result_by_type.setdefault(r.content_type(), [])
                thistype.append(r)
            # TODO: do filtering in the search query
            content['results'] = dict(
                places=result_by_type.get('places.place', []),
                events=[result for result in result_by_type.get('events.event', [])
                            if result.object.dtend > timezone.now()],
                specials=[result for result in result_by_type.get('specials.special', [])
                            if result.object.dexpires > timezone.now().date()],
                news_articles=result_by_type.get('news.article', []),
                chatter_posts=result_by_type.get('chatter.post', []),
            )

        # doesn't do anything, but will remind me in case this inherits from something else
        content.update(self.extra_context())

        context = PageContext(self.request,
            page_title="Scenable | Oakland Search",
            content_dict=content)
        return render_to_response(self.template, context_instance=context)

    def __call__(self, request, *args, **kwargs):
        # lock non beta testers out
        if not request.user or not request.user.is_authenticated():
            return to_login(request)
        return super(PageSiteSearch, self).__call__(request, *args, **kwargs)


class PageFilteredFeed(SearchView):
    '''
    Base view class for filtered feeds. Only works with ViewModels right now.
    Will need to change once VM mess is gotten rid of.
    '''
    def __init__(self, model_class, viewmodel_class, *args, **kwargs):
        '''
        Fixes the SearchQuerySet to only search over a particular model.
        '''
        self.model_class = model_class
        self.viewmodel_class = viewmodel_class
        sqs = kwargs.get('searchqueryset', SearchQuerySet())
        kwargs['searchqueryset'] = sqs.models(model_class)
        super(PageFilteredFeed, self).__init__(*args, **kwargs)

    def __call__(self, request, *args, **kwargs):
        # lock non beta testers out
        if not request.user or not request.user.is_authenticated():
            return to_login(request)
        return super(PageFilteredFeed, self).__call__(request, *args, **kwargs)

    def get_results(self):
        '''
        Ensures all results are returned if there is no query.

        Returns a list of the actual objects searched for, not SearchResult objects.
        '''
        if not self.query:
            instances = self.hacked_unfiltered()
        else:
            instances = self.hacked_filtered()
        return [self.viewmodel_class(instance, user=self.request.user) for instance in instances]

    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        (paginator, page) = self.build_page()
        items_json = sanitize_json(json.dumps([item.serialize() for item in page.object_list]))

        content = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'suggestion': None,
            'items_json': items_json
        }

        content.update(self.extra_context())
        return render_to_response(self.template, context_instance=self.get_page_context(content))

    def hacked_filtered(self):
        return [result.object for result in self.form.search()]

    def hacked_unfiltered(self):
        '''
        Temporary hack to get a list of unfiltered results. Will either be
        self.model_class.objects.all() or
        self.model_class.listed_objects.all().

        Necessary because self.searchqueryset.all() seems to be buggy.
        '''
        raise NotImplementedError('calling an abstract base class')

    def get_page_context(self, content):
        '''
        Override per feed page.
        '''
        return PageContext(self.request, content_dict=content)


### URL-LINKED VIEWS ###
@login_required
def page_home(request):
    return redirect(reverse('now'))


### STATIC PAGES ###
def page_static_about_oakland(request):
    context = PageContext(request, page_title="Scenable | About Oakland")
    return render_to_response('static_pages/about_oakland.html', context_instance=context)


def page_static_team(request):
    context = PageContext(request, page_title="Scenable | The Team")
    return render_to_response('static_pages/team.html', context_instance=context)


def page_static_mission(request):
    context = PageContext(request, page_title="Scenable | Our Mission")
    return render_to_response('static_pages/mission.html', context_instance=context)
