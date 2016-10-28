from node_processor_abstract import NodeProcessorAbstract
from switchables import Interface
from common.singleton import Singleton


class NodeProcessorInterface(Interface):
    __metaclass__ = Singleton

    def __init__(self):
        Interface.__init__(self, NodeProcessorAbstract)
