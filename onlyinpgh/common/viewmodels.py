from onlyinpgh.common.core.viewmodels import RenderableViewModel

class FeedViewModel(RenderableViewModel):
	'''
	Base ViewModel for Feeds. Abstract base class, requires subclasses
	to define a value for class_name.
	'''
	template_name = 'feed.html'
	class_name = None
	def __init__(self):
		self.items = []

	def to_data(self,*args,**kwargs):
		'''Lets base to_data to most of the work, then adds class_name to data.'''
		cleaned_dict = super(FeedViewModel,self).to_data(*args,**kwargs)
		cleaned_dict['class_name'] = self.class_name
		return cleaned_dict

	def to_html(self,request=None):
		'''Ensures class name is defined'''
		if not self.class_name:
			raise NotImplementedError('FeedViewModel subclasses must define the class_name variable!')
		return super(FeedViewModel,self).to_html(request)

class FeedCollection(RenderableViewModel):
	template_name = 'feed_collection.html'
	@classmethod
	def init_from_feeds(cls,feed_tuples):
		'''
		Initialize from list of (label,FeedViewModel) tuples.
		'''
		inst = cls()
		inst.feeds = [ {'label': label,
						'feed_view': feed} 
						for label,feed in feed_tuples ]
		return inst