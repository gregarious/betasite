from onlyinpgh.common.core.viewmodels import ViewModel


class PublicProfile(ViewModel):
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
    def __init__(self, user):
        self.profile = user.get_profile()

    def to_data(self, *args, **kwargs):
        '''
        Returns the public members of the user profile. Note that
        this means that fb/twitter ids will not be returned if
        their respective public flags are set to False.
        '''
        data = super(PublicProfile, self).to_data(*args, **kwargs)
        profile_data = data.get('profile')
        keepers = set(('id', 'username', 'display_name', 'points', 'avatar_url'))
        # also keep the fb/twitter ids if user wants them public
        if profile_data.get('fb_id_public'):
            keepers.add('fb_id')
        if profile_data.get('twitter_username_public'):
            keepers.add('twitter_username')

        for k in profile_data.keys():
            if k not in keepers:
                profile_data.pop(k)

        return data
