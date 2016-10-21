from switchables import Switchable
import logging
import socket
import os
from common.loggers import LoggingContext


class NodeProcessorAbstract(Switchable):
    name = None

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

    def init(self):
        self.setup_name()

    def setup_name(self):
        self.name = socket.gethostbyaddr(socket.gethostname())[0]
        if "_CONDOR_SLOT" in os.environ:
            self.name = os.environ.get("_CONDOR_SLOT", '') + "@" + self.name

    def copy_previous(self, previous):
        self.setup_name()

    def print_packages(self):
        log = logging.getLogger('node')
        rootlog = logging.getLogger()
        log.info("Installed packages:")
        with LoggingContext(rootlog, max(logging.INFO, rootlog.getEffectiveLevel())):
            # suppress pip debug messages
            import pip
            packages = pip.get_installed_distributions()
        for pack in packages:
            log.info("%s (%s)" % (pack.key, pack.version))

    def print_info(self):
        log = logging.getLogger('node')
        log.info("Node related information.")
        log.info("Node name: %s" % self.name)
        log.info("CPU frequency: %d MHz" % self.get_cpu())
        log.info("CPU cores: %d" % self.get_cores())
        log.info("RAM: %d MB" % self.get_mem())
        log.info("Disk: %d MB" % self.get_disk())
        self.print_packages()

    def can_obtain_job(self):
        return True

    def get_cpu(self):
        pass

    def get_cores(self):
        pass

    def get_mem(self):
        pass

    def get_disk(self, path='.'):
        pass
