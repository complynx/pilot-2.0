from node_processor_abstract import NodeProcessorAbstract
from switchables import Interface


class NodeProcessorInterface(Interface):
    def __init__(self):
        Interface.__init__(self, NodeProcessorAbstract)
