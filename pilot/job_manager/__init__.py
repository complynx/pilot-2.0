from default import JobManagerDefault
from switchables import Interface


class JobManagerInterface(Interface):
    def __init__(self):
        Interface.__init__(self, JobManagerDefault)
