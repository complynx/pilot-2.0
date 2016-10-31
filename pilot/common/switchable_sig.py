from switchables import Switchable
from signalslot import Signal


class SwitchableWithSignals(Switchable):
    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)

        if previous is None:
            self.init()
        else:
            self.copy_previous(previous)

    def init(self):
        for i in dir(self):
            val = getattr(self, i)
            if isinstance(val, Signal):
                val.emmitter = self.interface
                val.name = self.interface.__class__.__name__ + "." + i

    def copy_previous(self, previous):
        for i in dir(previous):
            val = getattr(previous, i)
            if isinstance(val, Signal):
                setattr(self, i, val)
