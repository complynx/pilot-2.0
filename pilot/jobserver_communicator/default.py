from switchables import Switchable
from common.signalslot import Signal


class JobserverCommunicator(Switchable):
    pilot = None
    got_new_job = Signal()
    got_job_state = Signal()

    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)
        if previous is not None:
            self.copy_previous(previous)
        else:
            self.init()

    def init(self):
        pass

    def copy_previous(self, previous):
        for i in ['pilot', 'got_new_job', 'got_job_state']:
            setattr(self, i, getattr(previous, i))

    def setup(self, pilot):
        self.pilot = pilot

    def get_job(self):
        return None

    def send_job_state(self, job):
        return None
