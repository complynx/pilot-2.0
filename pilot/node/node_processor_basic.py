import node_processor_abstract
import psutil
import cpuinfo


class NodeProcessorBasic(node_processor_abstract.NodeProcessorAbstract):
    def __init__(self, interface, previous=None):
        node_processor_abstract.SwitchableWithSignals.__init__(self, interface, previous)
        if previous is None:
            self.init()
        else:
            self.copy_previous(previous)

    def get_cpu(self):
        return float(cpuinfo.get_cpu_info()['hz_actual_raw'][0]) / 1000000.

    def get_cores(self):
        return cpuinfo.get_cpu_info()['count']

    def get_mem(self):
        return float(psutil.virtual_memory().total) / 1024. / 1024.

    def get_disk(self, path='.'):
        return float(psutil.disk_usage(path).free) / 1024. / 1024.
