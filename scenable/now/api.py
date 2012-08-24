from tastypie import http
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from sorl.thumbnail import get_thumbnail

from django.conf.urls import url

import random

from .models import FeaturedImage, Notice


class SingleObjectMixin(object):
    '''
    AB Class for a ModelResource mixin that is designed to return a single
    object from the queryset from a custom-defined endpoint.
    '''
    def override_urls(self):
        '''
        Need to override and call self.wrap_view('single_mixin_dispatch')
        '''
        pass

    def mixin_get_obj(self, request):
        '''
        Need to override and return a single object of the
        self._meta.queryset type.

        Should return http.HttpNotFound() or http.HttpMultipleChoices()
        if respective errors occur.
        '''
        pass

    def single_mixin_dispatch(self, request, **kwargs):
        # boilerplate from tastypie/resource.py: Resource.dispatch
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.is_authorized(request)
        self.throttle_check(request)

        obj = self.mixin_get_obj(request)

        # boilerplate from tastypie/resource.py: Resource.get_detail
        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)

        # Add the throttled request.
        self.log_throttled_access(request)

        return self.create_response(request, bundle)


class LatestEndpointMixin(SingleObjectMixin):
    '''
    Adds a "/latest" endpoint to the API that returns a resource for the
    latest created object in the queryset (hardcoded to use dtcreated).
    '''
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/latest%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('single_mixin_dispatch'), name="api_notice_latest"),
        ]

    def mixin_get_obj(self, request):
        try:
            return self._meta.queryset.order_by('-dtcreated')[0]
        except IndexError:
            return http.HttpNotFound()


class RandomEndpointMixin(SingleObjectMixin):
    '''
    Adds a "/random" endpoint to the API that returns a resource for a
    random object in the queryset (hardcoded to use dtcreated).
    '''
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/random%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('single_mixin_dispatch'), name="api_notice_latest"),
        ]

    def mixin_get_obj(self, request):
        try:
            idx = random.randint(0, self._meta.queryset.count() - 1)
            return self._meta.queryset.order_by('-dtcreated')[idx]
        except ValueError:  # occurs on a randint(0,-1) call
            return http.HttpNotFound()
        except IndexError:  # shouldn't happen
            return http.HttpNotFound()


### API RESOURCES ###
class FeaturedImageResource(RandomEndpointMixin, ModelResource):
    class Meta:
        queryset = FeaturedImage.objects.all()
        allowed_methods = ['get']

    def dehydrate_image(self, bundle):
        '''
        Overrides the default of strings as serialized DecimalField values
        '''
        if not bundle.obj.image:
            return bundle.obj.image

        size = bundle.request.GET.get('size', '700x450')
        crop = bundle.request.GET.get('crop', 'center')

        return get_thumbnail(bundle.obj.image, size, crop=crop)


class NoticeResource(LatestEndpointMixin, ModelResource):
    class Meta:
        queryset = Notice.objects.all()
        allowed_methods = ['get']
