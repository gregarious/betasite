from onlyinpgh.common.core.viewmodels import ViewModel


class FeedCollection(ViewModel):
    def __init__(self, feed_tuples, request=None):
        '''
        Initialize from list of (label,FeedViewModel) tuples.
        '''
        super(FeedCollection, self).__init__(request=request)
        self.feeds = [{'label': label, 'feed_view': feed}
                        for label, feed in feed_tuples]
        print 'FeedCollection init: ', self.__dict__
