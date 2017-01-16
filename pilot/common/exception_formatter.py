import logging
import sys
import traceback
import threading


def caught(exception, exc_info=sys.exc_info()):
    """
    Exception formatter and logger.

    Logs a caught exception into the Logger 'Exception' according to logging configs.
    Unlike python logger, this will output stack trace in the reverse way (easier to look) and with better readability.
    Also, prints out thread information, because this is very useful in massively threaded case.

    :param (Exception) exception:
    :param exc_info: Optional, the output of the `sys.exc_info()`, if it was caught earlier.
    """

    try:
        module_name = exc_info[0].__name__
    except AttributeError:
        module_name = '{none}'
    try:

        tb = list(reversed(traceback.extract_tb(exc_info[2])))

        tb_str = "\n"
        for i in tb:
            tb_str += '{file}:{line} (in {module}): {call}\n'.format(file=i[0],
                                                                     line=i[1],
                                                                     module=i[2],
                                                                     call=i[3])
        # logger.debug("Traceback:" + tb_str + " ----")
        thread = threading.currentThread()
        msg = "%s: %s" % (module_name, exception.message)
        msg += "\nTraceback: (latest call first)" + tb_str + "Thread: %s(%d)" % (thread.getName(), thread.ident)

        logger = logging.getLogger('Exception')
        logger.handle(logger.makeRecord(logger.name, logging.ERROR, tb[0][0], tb[0][1], msg, (), None, tb[0][2]))
    except Exception as e:
        logger = logging.getLogger('CRITICAL')
        logger.handle(logger.makeRecord(logger.name, logging.CRITICAL, "caught()", 40, e.message, (), None, None))
