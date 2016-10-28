"""
This is the main entrance point.
"""
from pilot import Pilot
import sys
import time
from common.async_decorator import async
import threading
import traceback
from common.exception_formatter import caught


@async(daemon=True)
def debug_stack_threading():
    time.sleep(1000)
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    print "\n".join(code)
    return


@async
def test():
    tuple()[0]


if __name__ == "__main__":
    try:
        pilot = Pilot(sys.argv)
        debug_stack_threading()
        pilot.start()
        pilot.join()
        test()
    except Exception as e:
        caught(e)
