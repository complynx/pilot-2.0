from default import ServerCommunicator
from switchables import Interface


class ServerCommunicatorInterface(Interface):
    def __init__(self):
        Interface.__init__(self, ServerCommunicator)
