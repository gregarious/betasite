from django.template import Context, RequestContext
from django.template.loader import get_template


class SelfRenderingView(object):
    template_name = None

    def self_render(self,request=None):
        '''
        Render the class's template with all instance variables passed in
        as the Context.
        '''
        if not self.template_name:
            raise NotImplementedError('SelfRenderingView subclasses must declare a template_name class variable!')
        context = self.to_context(request)
        return get_template(self.template_name).render(context)

    def to_context(self,request=None):
        if request:
            return RequestContext(request,self.__dict__)
        else:
            return Context(self.__dict__)

class FeedItem(SelfRenderingView):
	@classmethod
	def render_feed_from_blocks(cls,item_blocks,dom_class,request=None):
		'''
		Given a list of rendered feed item blocks, pastes them together
		using feed.html.
		''' 
		# feed these rendered blocks into feed.html
		vbls = dict(items=item_blocks,
					class_name=dom_class)
		feed_context = RequestContext(request,vbls) if request else Context(vbls)
		feed_html = get_template('feed.html').render(feed_context)
		return feed_html
