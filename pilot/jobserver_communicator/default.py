from switchables import Switchable
from common.signalslot import Signal
from common.async_decorator import async
import urllib2
import urllib
import logging
import json
from minipilot.job_description_fixer import description_fixer
import threading

log = logging.getLogger('JobserverCommunicator')


class JobserverCommunicator(Switchable):
    args = None
    got_new_job = Signal()
    got_job_state = Signal()
    ssl_context = None
    job_server = None
    queue_name = None
    job_queue = None
    job_tag = None
    _async_get_job = threading.Lock()

    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)
        if previous is not None:
            self.copy_previous(previous)
        else:
            self.init()

    def init(self):
        pass

    def copy_previous(self, previous):
        for i in ['pilot', 'ssl_context', 'job_server', 'queue', 'job_tag', 'job_queue']:
            setattr(self, i, getattr(previous, i))
        for i in dir(previous):
            val = getattr(previous, i)
            if isinstance(val, Signal):
                setattr(self, i, val)

        if self.args is not None and self.queue_name is None:
            self.setup(self.args, self.job_queue)

    def setup(self, args, queue):
        global log
        log = logging.getLogger('JobserverCommunicator')
        self.args = args
        self.job_queue = queue
        try:
            import ssl
            self.ssl_context = ssl.create_default_context(capath=args['capath'], cafile=args['cacert'])
        except Exception as e:
            log.warn('SSL communication is impossible due to SSL error:')
            log.warn(e.message)
            pass
        self.job_server = '%s:%d' % (args['job_server'][0], args['job_server'][1])
        self.queue_name = self.args['queue']
        self.job_tag = self.args['job_tag']

    @async
    def get_job(self, *_):
        if not self._async_get_job.acquire(False):
            return
        try:
            log.info("Trying to get a job from queue %s with tag %s" % (self.queue_name, self.job_tag))
            log.info("Using server %s" % self.job_server)
            node = self.args['node']
            request = urllib2.Request("https://%s/server/panda/getJob" % self.job_server, urllib.urlencode({
                'cpu': node.get_cpu(),
                'mem': node.get_mem(),
                'node': node.name,
                'diskSpace': node.get_disk(),
                'getProxyKey': False,  # do we need it?
                'computingElement': self.queue_name,
                'siteName': self.queue_name,
                'workingGroup': '',  # do we need it?
                'prodSourceLabel': self.job_tag
            }))
            request.add_header('Accept',
                               'application/json;q=0.9,text/html,application/xhtml+xml,application/xml;q=0.7,*/*;q=0.5')
            request.add_header('User-Agent', self.args['user_agent'])
            try:
                f = urllib2.urlopen(request, context=self.ssl_context)
                result = json.loads(f.read())
                code = result['StatusCode'] if 'StatusCode' in result else result['status_code']
                if code == 0:
                    job_desc = description_fixer(result)
                    log.info("Got new job description, job id %s" % job_desc["job_id"])
                    self.got_new_job.async(job_desc)
                else:
                    log.info("Returned status code = %d", code)
            except urllib2.HTTPError as e:
                log.warn("Server returned error %d:" % e.code)
                log.warn(e.read())
            except urllib2.URLError as e:
                log.warn("Could not reach the server %s:" % e.reason)
        finally:
            self._async_get_job.release()

    def get_job_from_file(self, file_name):
        with open(file_name) as f:
            j = json.load(f)
            log.info("Successfully loaded file and parsed.")
            job_desc = description_fixer(j)
            log.info("Got new job description, job id %s" % job_desc["job_id"])
            self.got_new_job.async(job_desc)

    def send_job_state(self, job):
        pass
