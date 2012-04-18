from django.template import Context


class PublicProfile(Context):
    '''
        profile
            id
            username
            display_name
            points
            avatar_url
            fb_id (optional)
            twitter_username (optional)
    '''
    def __init__(self, user, **kwargs):
        profile = user.get_profile()
        # unpack profile and fix the variables to the root of the PublicProfile context
        vbls = dict([(k, v) for k, v in profile.__dict__.items() if not k.startswith('_')])
        super(PublicProfile, self).__init__(vbls, **kwargs)
