from django.template import Context


class PublicProfile(Context):
    '''
    Context for public profile information.

    For now, just a copy of a UserProfile, but this will change.
    '''
    def __init__(self, user, **kwargs):
        profile = user.get_profile()
        # just do a direct copy of the user profile for now.
        vbls = dict([(k, v) for k, v in profile.__dict__.items() if not k.startswith('_')])
        super(PublicProfile, self).__init__(vbls, **kwargs)
