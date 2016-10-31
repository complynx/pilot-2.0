from default import JobserverCommunicator
from switchables import Interface


class JobserverCommunicatorInterface(Interface):
    def __init__(self):
        # type: () -> JobserverCommunicator
        Interface.__init__(self, JobserverCommunicator)
