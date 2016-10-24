from switchables import Switchable
import logging
import socket
import os
from common.loggers import LoggingContext
from common.signalslot import Signal
from common.async_decorator import async


class NodeProcessorAbstract(Switchable):
    name = None
    has_available_slots = Signal()
    jobs_running = []
    max_available_jobs = 1
    jobs_limit = -1
    jobs_count = 0

    def __init__(self, interface, previous=None):
        Switchable.__init__(self, interface, previous)
        # # it's abstract. Removing this
        # if previous is None:
        #     self.init()
        # else:
        #     self.copy_previous(previous)
        have_basics = False
        try:
            import cpuinfo  # NOQA: F401 we are testing it for existence
            import psutil  # NOQA: F401 we are testing it for existence
            have_basics = True
        except ImportError:
            pass
        if have_basics:
            interface.switchable_load('node_processor_basic')
            return
        else:
            interface.switchable_load('node_processor_unix')
            return

    @async
    def request_slots(self):
        available = self.max_available_jobs - len(self.jobs_running)
        if available > 0:
            self.has_available_slots(available)

    @async
    def push_job(self, job, queue):
        import json
        log = logging.getLogger('node')
        self.jobs_running.append(job)
        log.debug("Have jobs to run:\n" + json.dumps(job, indent=4))

    def init(self):
        self.setup_name()

    def setup_name(self):
        self.name = socket.gethostbyaddr(socket.gethostname())[0]
        if "_CONDOR_SLOT" in os.environ:
            self.name = os.environ.get("_CONDOR_SLOT", '') + "@" + self.name

    def copy_previous(self, previous):
        self.setup_name()
        for i in ['jobs_count', 'jobs_limit', 'max_available_jobs', 'jobs_running']:
            setattr(self, i, getattr(previous, i))
        for i in dir(previous):
            val = getattr(previous, i)
            if isinstance(val, Signal):
                setattr(self, i, val)

    def print_packages(self):
        log = logging.getLogger('node')
        rootlog = logging.getLogger()
        log.info("Installed packages:")
        try:
            with LoggingContext(rootlog, max(logging.INFO, rootlog.getEffectiveLevel())):
                # suppress pip debug messages
                import pip
                packages = pip.get_installed_distributions()
            for pack in packages:
                log.info("%s (%s)" % (pack.key, pack.version))
        except Exception as e:
            log.warn("Failed to list installed packages. It may not be the issue, though.")
            log.warn(e.message)
            pass

    def print_ssl_version(self):
        log = logging.getLogger('node')
        try:
            import ssl
            log.info("SSL version: " + ssl.OPENSSL_VERSION)
        except ImportError:
            log.warn("No SSL support on this machine. If pilot needs direct communication with a server, it failes.")

    def print_info(self):
        log = logging.getLogger('node')
        log.info("Node related information.")
        log.info("Node name: %s" % self.name)
        log.info("CPU frequency: %d MHz" % self.get_cpu())
        log.info("CPU cores: %d" % self.get_cores())
        log.info("RAM: %d MB" % self.get_mem())
        log.info("Disk: %d MB" % self.get_disk())
        self.print_packages()
        self.print_ssl_version()

    def get_cpu(self):
        pass

    def get_cores(self):
        pass

    def get_mem(self):
        pass

    def get_disk(self, path='.'):
        pass
