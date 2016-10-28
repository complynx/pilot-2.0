import node_processor_abstract
import os
import pipes
import string


class NodeProcessorBasic(node_processor_abstract.NodeProcessorAbstract):
    def __init__(self, interface, previous=None):
        node_processor_abstract.SwitchableWithSignals.__init__(self, interface, previous)
        if previous is None:
            self.init()
        else:
            self.copy_previous(previous)

    def get_cpu(self):
        with open("/proc/cpuinfo", "r") as fd:
            lines = fd.readlines()
        for line in lines:
            if not string.find(line, "cpu MHz"):
                return float(line.split(":")[1])
        return 0.

    def get_cores(self):
        with open("/proc/cpuinfo", "r") as fd:
            lines = fd.readlines()
        inc = 0
        for line in lines:
            if not string.find(line, "cpu MHz"):
                inc += 1
        return inc

    def get_mem(self):
        with open("/proc/meminfo", "r") as fd:
            mems = fd.readline()
            while mems:
                if mems.upper().find("MEMTOTAL") != -1:
                    return float(mems.split()[1]) / 1024
                mems = fd.readline()
        return 0.

    def get_disk(self, path='.'):
        diskpipe = os.popen("df -mP %s" % pipes.quote(path))  # -m = MB
        disks = diskpipe.read()
        if not diskpipe.close():
            return float(disks.splitlines()[1].split()[3])
        return 0.
