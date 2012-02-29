from onlyinpgh.common.core.viewmodels import RenderableViewModel

class TagList(RenderableViewModel):
	template_name = 'tags/tag-list.html'
	def __init__(self,tags):
		'''takes in a iterable of Tag objects'''
		self.tags = tags