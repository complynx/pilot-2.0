from abstract import JobRequesterAbstract
from single import SingleJobQueue
from switchables import Interface


class JobRequesterInterface(Interface):
    def __init__(self):
        Interface.__init__(self, SingleJobQueue, JobRequesterAbstract)
