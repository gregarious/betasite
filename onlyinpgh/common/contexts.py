from django.template import Context, RequestContext


class PageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_section, content_dict={}, **kwargs):
        '''
        current_section: string among 'places', 'events', 'news', etc...
        content_dict: context variables for main_context
        '''
        header_context = Context({
            'current_section': current_section,
            'search_form': None,
        })
        sidebar_context = Context({})
        main_context = Context(content_dict)
        footer_context = Context({})

        super(PageContext, self).__init__(request, dict(
            header_context=header_context,
            sidebar_context=sidebar_context,
            main_context=main_context,
            footer_context=footer_context),
        **kwargs)
