class PublicProfile(object):
    '''
    For now, just a copy of a UserProfile, but this will change.
    '''
    def __init__(self, user, **kwargs):
        fields = ('display_name', 'avatar_url', 'points', 'fb_id',
                  'fb_id_public', 'twitter_username', 'neighborhood',
                  'twitter_username_public', 'gender', 'birth_year')
        profile = user.get_profile()
        for attr in fields:
            setattr(self, attr, getattr(profile, attr))
