from default import DefaultJobQueue
from switchables import Interface
from common.singleton import Singleton


class JobQueueInterface(Interface):
    __metaclass__ = Singleton

    def __init__(self):
        Interface.__init__(self, DefaultJobQueue)