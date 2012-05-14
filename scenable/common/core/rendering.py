from django.template.loader import get_template, render_to_string
from django.utils.safestring import mark_safe

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

def _wrap_content(content, tag_type=None, class_label=None, id_label=None, attrs={}):
    '''
    Helper for wrapping content in elements.
    '''
    if not tag_type:
        return content

    attrs.update({'class': class_label, 'id': id_label})
    attr_strs = [('%s="%s"' % (key, str(val).replace(r'"', r'\"')))
                    for key, val in attrs.items() if val is not None]
    return mark_safe('<%s %s>\n%s\n</%s>' % (tag_type, ' '.join(attr_strs), content, tag_type))


def render_list(elements, tag_type='ul', class_label=None, id_label=None, attrs={}):
    '''
    Simple helper to render a list of elements. Will wrap the elements
    in an outer wrapper with attributes as specified.
    '''
    return _wrap_content('\n'.join(elements),
                            tag_type=tag_type, class_label=class_label,
                            id_label=id_label, attrs=attrs)


def render_safe(template, context_instance=None, **kwargs):
    '''
    Wrapper around Django's render_to_string function. Uses kwargs instead of
    dictionary.

    Only use templates that are safe to mark as safe!
    '''
    return mark_safe(render_to_string(template, kwargs, context_instance))


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

    return mark_safe(_wrap_content(rendered, tag_type=tag_type,
        class_label=class_label, id_label=id_label, attrs=attrs))


def render_viewmodels_as_ul(items, item_template,
                            container_class_label=None,
                            item_class_label='item'):
    '''
    Renders a collection of ViewModel objects in an unordered list.

    Returns a SafeString of the rendered content.
    '''
    rendered_items = [render_viewmodel(item, template=item_template, tag_type='li',
                                        class_label=item_class_label)
                        for item in items]
    return mark_safe(render_list(rendered_items, tag_type='ul', class_label=container_class_label))
