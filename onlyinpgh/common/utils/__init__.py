import re

url_pattern = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def process_external_url(url):
    url_p = re.compile(url_pattern)
    if not url_p.match(url):
        url = 'http://' + url
        if not url_p.match(url):    # if that didn't work, blank out the url
            url = ''
    return url


def get_or_none(manager, **kwargs):
    '''
    Wrapper aroudn a get call that will silently return
    None if the object is not found.
    '''
    try:
        return manager.get(**kwargs)
    except manager.model.DoesNotExist:
        return None
