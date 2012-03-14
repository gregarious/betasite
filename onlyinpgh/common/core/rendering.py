from django.template.loader import get_template

# work in progress. don't use self_render template tag till fixed

# class Renderable(object):
#     '''
#     Wrapper class to allow encapsulating a ViewModel (or any object that
#     implements a to_context method) with a template responsible for rendering
#     its contents.

#     Gives view functions an easy way to render a ViewModel with customizable
#     container attributes. Also allows for the self_render template tag to be
#     used to render the object.

#     See render_context docstring for argument info.
#     '''
#     def __init__(self, contexable_obj, template,
#                  tag_type='', class_label='', id_label='', attrs={}):
#         self.contexable_obj = contexable_obj
#         self.template = template
#         self.tag_type = tag_type
#         self.class_label = class_label
#         self.id_label = id_label
#         self.attrs = attrs

#         # inject a _template attribute for self_render template tag
#         setattr(self.contexable_obj, '_template', template)
#         setattr(self.contexable_obj, '_template', template)


#     def to_context(self, *args, **kwargs):
#         return self.contexable_obj.to_context(*args, **kwargs)

#     def render(self):
#         return render_context(self.contexable_obj.to_context, self.template,
#                                 tag_type=tag_type, class_label=class_label,
#                                 id_label=id_label, attrs=attrs)


def render_viewmodel(viewmodel, template, tag_type=None, class_label=None, id_label=None, attrs={}):
    '''
    Returns a fully-rendered template given the context provided by the
    input object's to_context method.

    If tag_type is present, the rendered template will be wrapped in an
    element described by tag_type, class_label, id_label, and attrs.

    Arguments:
    - context: django.template.Context object
    - template: django.template.Template object
                or template name for a template loader
    - tag_type: tag name
    - class_label: value for class attribute
    - id_label: value for id attribute
    - attrs: miscellaneous attribute key: value dict

    All attribute values are assumed to already be html-escaped.

    Important: do not add class or id attributes to the attr dict. They will
    be overridden. Use id_label and class_label for this purpose.
    '''
    try:
        rendered = template.render(viewmodel.to_context())
    except AttributeError:
        rendered = get_template(template).render(viewmodel.to_context())

    if tag_type:
        attrs.update({'class': class_label, 'id': id_label})
        attr_strs = [('%s="%s"' % (key, str(val).replace(r'"', r'\"')))
                        for key, val in attrs.items() if val is not None]
        rendered = '<%s %s>\n%s\n</%s>' % (tag_type, ' '.join(attr_strs), rendered, tag_type)
    return rendered