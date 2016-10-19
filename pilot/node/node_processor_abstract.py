from switchables import Switchable
import logging


class NodeProcessorAbstract(Switchable):
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
        pass

    def copy_previous(self, previous):
        pass

    def print_info(self):
        log = logging.getLogger('node')
        log.info("CPU frequency: %d MHz" % self.get_cpu())
        log.info("CPU cores: %d" % self.get_cores())
        log.info("RAM: %d MB" % self.get_mem())
        log.info("Disk: %d MB" % self.get_disk())

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
