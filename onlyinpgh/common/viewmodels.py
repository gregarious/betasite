from onlyinpgh.common.core.viewmodels import ViewModel


class FeedCollection(ViewModel):
    def __init__(self, **kwargs):
        '''
        kwargs should be a list of feed item lists. The key names
        in this constructor will become the keys of the data.
        '''
        super(FeedCollection, self).__init__()
        for key, items in kwargs.items():
            setattr(self, key, items)
