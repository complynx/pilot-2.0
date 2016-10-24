from switchables import Switchable
from jobserver_communicator import JobserverCommunicatorInterface
from common.signalslot import Signal
import logging


class DefaultJobQueue(Switchable):
    args = None
    communicator = None
    jobs_pending = []
    has_pending_jobs = Signal()
    has_available_slots = Signal()
    start_job = Signal()

    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)

        if previous is None:
            self.init()
        else:
            self.copy_previous(previous)

    @property
    def log(self):
        return logging.getLogger(self.__class__.__name__)

    def init(self):
        self.has_pending_jobs.connect(self.log_jobs)
        pass

    def copy_previous(self, previous):
        for i in dir(previous):
            val = getattr(previous, i)
            if isinstance(val, Signal):
                setattr(self, i, val)

    def log_jobs(self):
        import json
        for i in self.jobs_pending:
            self.log.debug("Pending job: \n%s" % json.dumps(i, indent=4))

    def setup(self, args):
        self.args = args
        self.set_server_communicator()

    def fill_node_slots(self, number):
        while number > 0:
            if len(self.jobs_pending) == 0:
                break
            job = self.jobs_pending.pop()

            self.start_job(job, self.interface)
            number -= 1
        if number:
            self.has_available_slots(number)

    def get_job(self):
        self.communicator.get_job()

    def push_job(self, job_desc):
        if self.validate_job(job_desc):
            self.jobs_pending.append(job_desc)
            self.has_pending_jobs.async()

    def validate_job(self, job):
        return True

    def load_from_file(self, file_name):
        self.communicator.get_job_from_file(file_name)

    def set_server_communicator(self):
        self.communicator = JobserverCommunicatorInterface()
        self.communicator.setup(self.args, self.interface)
        self.communicator.got_new_job.connect(self.interface.push_job)
        self.has_available_slots.connect(self.communicator.get_job)

    def has_empty_slots(self):
        return 0

    def graceful_shutdown(self):
        self.my_thread.graceful_shutdown()
        self.graceful_shutdown_jobs()

    def graceful_shutdown_jobs(self):
        pass
