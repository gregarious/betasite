from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse

from django.http import Http404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils import timezone
from django.contrib.sites.models import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from haystack.views import SearchView
from haystack.forms import SearchForm

from scenable.feedback.forms import GenericFeedbackForm
from scenable.common.utils.jsontools import sanitize_json
import json
import urlparse


# TODO: deprecated? Was only used for private beta
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


# TODO: consider moving page context stuff into a template context processor
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
            site_url=get_current_site(request).domain,
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
                            if result.object.dexpires is None or result.object.dexpires > timezone.now().date()],
                news_articles=result_by_type.get('news.article', []),
                chatter_posts=result_by_type.get('chatter.post', []),
            )

        # doesn't do anything, but will remind me in case this inherits from something else
        content.update(self.extra_context())

        context = PageContext(self.request,
            page_title="Scenable | Oakland Search",
            content_dict=content)
        return render_to_response(self.template, context_instance=context)


class PageFilterableFeed(SearchView):
    def __init__(self, searchqueryset, nosearch_queryset, template, viewmodel_class=None, *args, **kwargs):
        self.nosearch_queryset = nosearch_queryset
        self.template = template
        self.viewmodel_class = viewmodel_class
        self.search_used = False
        super(PageFilterableFeed, self).__init__(
            template=template,
            form_class=SearchForm,
            searchqueryset=searchqueryset,
            *args, **kwargs)

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
            return self.nosearch_queryset

    def build_page(self):
        """
        Paginates the results appropriately. Pages will contains an actual
        model object, despite ragardless of whether the results returned
        were model instances or search results.
        """
        if self.search_used:
            processed_results = [result.object for result in self.results]
        else:
            processed_results = self.results

        if self.viewmodel_class:
            processed_results = [self.viewmodel_class(result) for result in processed_results]

        paginator = Paginator(processed_results, self.results_per_page)

        page_no = self.request.GET.get('page')
        try:
            page = paginator.page(page_no)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            # if page out of range, return last one
            page = paginator.page(paginator.num_pages)
        return page

    def get_page_context(self, request):
        '''
        Return a dict of extra context variables. Override this.
        '''
        return PageContext(self.request,
            current_section=None,
            page_title='Scenable')

    def create_response(self):
        page = self.build_page()

        content = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'items_json': sanitize_json(json.dumps([p.serialize() for p in page])),
        }

        context = self.get_page_context(self.request)
        return render_to_response(self.template, content, context_instance=context)


### URL-LINKED VIEWS ###
def page_oakland_home(request):
    return redirect(reverse('now'))

def page_home(request):
    if request.user.is_authenticated():
        return page_oakland_home(request)
    return redirect(reverse('about'))


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
