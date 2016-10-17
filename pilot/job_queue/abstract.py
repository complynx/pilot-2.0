from switchables import Switchable


class JobQueueAbstract(Switchable):
    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)
        # # it's abstract. Removing this
        # if previous is None:
        #     self.init()
        # else:
        #     self.copy_previous(previous)
