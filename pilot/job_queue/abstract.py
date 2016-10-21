from switchables import Switchable
from server_communicator import ServerCommunicatorInterface
import logging
log = logging.getLogger()


class JobQueueAbstract(Switchable):
    pilot = None
    node = None
    communicator = None
    my_thread = None

    def __init__(self, interface, previous=None):
        global log
        log = logging.getLogger('JobQueue')
        Switchable.__init__(self, interface, previous)

        # # it's abstract. Removing this
        # if previous is None:
        #     self.init()
        # else:
        #     self.copy_previous(previous)

    def setup(self, pilot, node):
        log.info("")
        self.pilot = pilot
        self.node = node
        self.set_server_communicator()

    def get_job(self):
        job = self.communicator.get_job()
        if job is not None:
            log.info("got job")
            if self.validate_job(job):
                log.info("job validated")

    def validate_job(self, job):
        return True

    def set_server_communicator(self):
        log.info("")
        self.communicator = ServerCommunicatorInterface()
        self.communicator.setup(self.pilot, self.node, self.interface)

    def has_empty_slots(self):
        return 0

    def graceful_shutdown(self):
        self.my_thread.graceful_shutdown()
        self.graceful_shutdown_jobs()

    def graceful_shutdown_jobs(self):
        pass
