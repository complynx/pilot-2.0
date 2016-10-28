from switchables import Interface
from common.singleton import Singleton
from default import SlotWorkerDefault


class SlotWorkerInterface(Interface):
    __metaclass__ = Singleton

    def __init__(self):
        Interface.__init__(self, SlotWorkerDefault)
