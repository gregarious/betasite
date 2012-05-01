from django.shortcuts import redirect, render_to_response
from django.core.urlresolvers import reverse

from django.http import Http404
from django.template import RequestContext

from haystack.views import SearchView
from haystack.forms import SearchForm


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
                print r, r.model_name
                thistype = result_by_type.setdefault(r.content_type(), [])
                thistype.append(r)
            content['results'] = dict(
                places=result_by_type.get('places.place', []),
                events=result_by_type.get('events.event', []),
                specials=result_by_type.get('specials.special', []),
                news_articles=result_by_type.get('news.article', []),
                chatter_posts=result_by_type.get('chatter.post', []),
            )

        # doesn't do anything, but will remind me in case this inherits from something else
        content.update(self.extra_context())

        context = PageContext(self.request,
            page_title="Scenable | Oakland Search",
            content_dict=content)
        return render_to_response(self.template, context_instance=context)


### URL-LINKED VIEWS ###
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
