from django.template import Context, RequestContext
from django.template.loader import get_template

url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

def get_or_none(manager,**kwargs):
    '''
    Wrapper aroudn a get call that will silently return
    None if the object is not found.
    '''
    try:
        return manager.get(**kwargs)
    except manager.model.DoesNotExist:
        return None

class ViewInstance(object):
    '''
    abstract base class to wrap and/or compose model instances for use
    in views.
    '''
    def __init__(self,instance,extract_m2m=False):
        '''
        Constructor copies all fields in the original model instance to
        this new instance. 

        Any fields that point to ManyToMany object managers (e.g. 
        GenericRelation, ManyToManyRelation) will simply have their
        field set to managers as well, unless extract_m2m is True.
        If so, the managers will be replaced with the results of an all() 
        call on themselves.
        '''
        self._orig_instance = instance
        for field in instance._meta.fields:
            setattr(self,field.name,getattr(instance,field.name))
        
        for field in instance._meta.many_to_many:
            # if the field value is a manager and we want to extract 
            # the related objects, do it now
            if extract_m2m:
                setattr(self,field.name,getattr(instance,field.name).all())
            else:
                setattr(self,field.name,getattr(instance,field.name))

class SelfRenderingView(object):
    template_name = None

    def render_template(self,request=None):
        '''
        Render the class's template with all instance variables passed in
        as the Context.
        '''
        if not cls.template_name:
            raise NotImplementedError('SelfRenderingView subclasses must declare a template_name class variable!')
        template = get_template(cls.template_name)
        context = self.to_context(request)
        return self._template.render(context)

    def to_context(request=None):
        if request:
            return RequestContext(request,self.__dict__)
        else:
            return Context(self.__dict__)