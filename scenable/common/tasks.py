# Project-wide celery tasks

from celery import task
from sorl.thumbnail import get_thumbnail


@task
def cache_image_thumbnail(model, pk, fieldname, size, crop='center'):
    instance = model._default_manager.get(pk=pk)
    image = getattr(instance, fieldname)
    if image:
        # if internal ImageField._file object is None, this will raise a
        # ValueError. Not sure how it gets in this state, but we just want to
        # punt if it happens.
        try:
            image.file
        except ValueError:
            pass
        else:
            image = get_thumbnail(image, size, crop=crop)
            return getattr(image, 'url')
    return None
