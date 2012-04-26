from tastypie.resources import Resource
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.bundle import Bundle
from onlyinpgh.events.models import Event
from onlyinpgh.events.viewmodels import EventData
from onlyinpgh.tags.resources import TagResource
from onlyinpgh.places.resources import PlaceFeedResource


### API RESOURCES ###
class EventFeedResource(Resource):
    id = fields.IntegerField('id')
    name = fields.CharField('name')
    image = fields.FileField('image')
    dtstart = fields.DateTimeField('dtstart')
    dtend = fields.DateTimeField('dtend')
    description = fields.CharField('description')
    tags = fields.ManyToManyField(TagResource, 'tags', full=True)
    place = fields.ForeignKey(PlaceFeedResource, 'place', full=True, null=True)
    place_primitive = fields.CharField('place_primitive')
    is_attending = fields.BooleanField('is_attending', null=True, default=False)

    class Meta:
        resource_name = 'event'
        object_class = EventData
        authorization = Authorization()

    def get_resource_url(self, bundle_or_obj):
        kwargs = {
            'resource_name': self._meta.resource_name,
        }

        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.id

        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url('api_dispatch_detail', kwargs=kwargs)

    def get_object_list(self, request):
        events = Event.objects.all()
        return [EventData(e, request.user) for e in events]

    def obj_get_list(self, request=None, **kwargs):
        events = Event.objects.filter(**kwargs)
        user = request.user if request else None
        return [EventData(e, user) for e in events]

    def obj_get(self, request=None, **kwargs):
        event = Event.objects.get(**kwargs)
        user = request.user if request else None
        return EventData(event, user)
