import logging
import sys
import traceback
import threading


def caught(e):
    exc_info = sys.exc_info()
    tb = list(reversed(traceback.extract_tb(exc_info[2])))

    tb_str = "\n"
    for i in tb:
        tb_str += '{file}:{line} (in {module}): {call}\n'.format(file=i[0],
                                                                 line=i[1],
                                                                 module=i[2],
                                                                 call=i[3])
    # logger.debug("Traceback:" + tb_str + " ----")
    thread = threading.currentThread()
    msg = "%s: %s" % (exc_info[0].__name__, e.message)
    msg += "\nTraceback: (latest call first)" + tb_str + "Thread: %s(%d)" % (thread.getName(), thread.ident)

    logger = logging.getLogger('Exception')
    logger.handle(logger.makeRecord(logger.name, logging.ERROR, tb[0][0], tb[0][1], msg, (), None, tb[0][2]))
