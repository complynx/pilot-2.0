from abstract import JobQueueAbstract
from single import SingleJobQueue
from switchables import Interface


class NodeProcessorInterface(Interface):
    def __init__(self):
        Interface.__init__(self, SingleJobQueue, JobQueueAbstract)
