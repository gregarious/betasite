from django.template import Context, RequestContext


class PageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_section, content_dict={}, **kwargs):
        '''
        current_section: string among 'places', 'events', 'news', etc...
        '''
        super(PageContext, self).__init__(request, **kwargs)
        self['header_context'] = Context({
            'current_section': current_section,
            'search_form': None,
        })
        self['sidebar_context'] = Context({})
        self['main_context'] = Context(content_dict)
        self['footer_context'] = Context({})


class ManagePageContext:
    '''
    Main context variable for every biz management page.
    '''
    pass
