from default import DefaultJobQueue
from switchables import Interface


class JobQueueInterface(Interface):
    def __init__(self):
        Interface.__init__(self, DefaultJobQueue)
