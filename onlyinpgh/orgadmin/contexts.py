from django.template import Context, RequestContext


class ManagePageContext(RequestContext):
    '''
    Used for main context variable for every main site page.
    '''
    def __init__(self, request, current_org=None, content_dict={}, **kwargs):
        '''
        content_dict: context variables for main_context
        '''
        main_context = Context(content_dict)

        super(ManagePageContext, self).__init__(request, dict(
                current_org=current_org,
                main_context=main_context
            ), **kwargs)
