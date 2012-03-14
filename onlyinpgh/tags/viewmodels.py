from onlyinpgh.common.core.viewmodels import ViewModel


class TagList(ViewModel):
    def __init__(self, tags):
        '''takes in a iterable of Tag objects'''
        self.tags = tags
