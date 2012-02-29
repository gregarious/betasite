'''
Module that sets up the ViewModel system.
'''
from django.template import Context, RequestContext
from django.template.loader import get_template
import json

class ViewModel(object):
	'''
	Abstract base class for ViewModels
	'''
	def to_data(self):
		'''
		Returns a serialization-friendly dict of the member variables
		stored in this ViewModel. Base class version simply strips out
		variables with names starting with an underscore and recursively
		calls to_data on any value that is a ViewModel instance. All 
		other values are assumed to be basic enough to be serializable.

		Classes derived from ViewModel that do not have member variables
		variables simple enough for this standard (e.g. Django models with 
		ForeignKeys) should override to_data.
		'''
		return basic_data_clean(self)

	def to_json(self):
		return json.dumps(self.to_data())

	def to_context(self,request=None):
		data = self.to_data()
		return RequestContext(request,data) if request else Context(data)

class RenderableViewModel(ViewModel):
	template_name = None

	# should be set to True only if template allows inner ViewModels to render themselves 
	inner_rendering = True		

	def to_data(self,flatten_viewmodels=True):
		'''
		Overridden method to allow treating ViewModels as primitives.

		Note that ViewModel.to_json still needs this method to flatten 
		everything, so the default value of flatten_viewmodels MUST be 
		True. to_context will make it False if inner_rendering dictates so.
		'''
		return basic_data_clean(self,flatten_viewmodels)					

	def to_context(self,request=None):
		'''
		Overridden method to allow treating ViewModels as primitives.
		'''		
		# flatten inner VMs if they aren't rendering themselves
		data = self.to_data(flatten_viewmodels=(not self.inner_rendering))	
		return RequestContext(request,data) if request else Context(data)

	def to_html(self,request=None):
		# TODO: remove
		if not self.template_name:
			raise NotImplementedError('RenderableViewModel subclasses must define the template_name class variable!')
		context = self.to_context(request)
		print self.to_json()
		return get_template(self.template_name).render(context)

def basic_data_clean(viewmodel,flatten_viewmodels=True):
	'''
	Simple function to convert a ViewModel's member variables to a data 
	dict. Will ignore underscore-led variable names.
	'''
	cleaned_dict = {}
	for key,val in viewmodel.__dict__.items():
		if key.startswith('_'):
			continue
		cleaned_dict[key] = _flatten(val,flatten_viewmodels)
	return cleaned_dict

def _flatten(obj,flatten_viewmodels=True):
	'''
	Flattens the given object to a serialization-friendly dict. Aware of
	the ViewModel to_data method interface and will defer to this function
	whenever possible. If intact_viewmodels is True, ViewModels will be 
	treated like primitives.

	Currently not built with bulletproof robustness in mind: only made to 
	handle primitives, lists, dicts, and ViewModels.
	'''
	# always assume object is a ViewModel first (implements to_data)
	if flatten_viewmodels:
		try:
			return obj.to_data()
		except AttributeError:
			pass
		
	# handle a dict
	try:
		return {k:_flatten(v,flatten_viewmodels) for k,v in obj.items()}
	except AttributeError:
		pass
	
	# handle an iterable like a tuple, set, or list as a list, but be sure 
	# to not to handle a string this way
	try:
		if not isinstance(obj,basestring):
			return [_flatten(v,flatten_viewmodels) for v in obj]
	except TypeError:
		pass
	
	# we're assuming anything that makes it to here is a primitive
	return obj

