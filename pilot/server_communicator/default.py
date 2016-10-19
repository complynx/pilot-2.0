from switchables import Switchable


class ServerCommunicator(Switchable):
    pilot = None
    node = None
    queue = None

    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)

    def setup(self, pilot, node, queue):
        self.pilot = pilot
        self.node = node
        self.queue = queue

    def get_job(self):
        return None

    def send_job_state(self, job):
        return None
