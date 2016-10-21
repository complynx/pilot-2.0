import abstract
import logging
log = logging.getLogger()


class DefaultJobRequester(abstract.JobRequesterAbstract):
    jobs = []
    max_jobs = 1

    def __init__(self, i, p=None):
        global log
        super(DefaultJobRequester, self).__init__(i, p)
        log = logging.getLogger('JobQueue')

    def set_max_jobs(self, new_max):
        log.info("new %d, old %d" % (new_max, self.max_jobs))
        self.max_jobs = new_max

    def has_empty_slots(self):
        l = len(self.jobs)
        log.info("Current %d, max %d" % (l, self.max_jobs))
        return max(self.max_jobs - l, 0)

    def graceful_shutdown_jobs(self):
        log.info("")
        [job.graceful_shutdown() for job in self.jobs]
