from abstract import PilotAbstract
from switchables import Interface


class PilotInterface(Interface):
    def __init__(self):
        Interface.__init__(self, PilotAbstract)
