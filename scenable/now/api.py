from tastypie.resources import ModelResource

from sorl.thumbnail import get_thumbnail

from .models import FeaturedImage, Notice


### API RESOURCES ###
class FeaturedImageResource(ModelResource):
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


class NoticeResource(ModelResource):
    class Meta:
        queryset = Notice.objects.all()
        allowed_methods = ['get']
