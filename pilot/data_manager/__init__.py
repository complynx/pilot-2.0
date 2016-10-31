from default import DataManagerDefault
from switchables import Interface


class DataManagerInterface(Interface):
    def __init__(self):
        # type: () -> DataManagerDefault
        Interface.__init__(self, DataManagerDefault)
