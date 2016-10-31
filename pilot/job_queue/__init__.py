from default import DefaultJobQueue
from switchables import Interface
from common.singleton import Singleton


class JobQueueInterface(Interface):
    __metaclass__ = Singleton

    def __init__(self):
        # type: () -> DefaultJobQueue
        Interface.__init__(self, DefaultJobQueue)
