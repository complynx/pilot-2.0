import signal
import os

sig_catchers = []
is_set_up = False

signals_reverse = {}

graceful_terminator = signal.SIGTERM

if os.name == "nt":
    graceful_terminator = signal.CTRL_BREAK_EVENT

    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    def _check_bool(result, func, args):
        if not result:
            raise ctypes.WinError(ctypes.get_last_error())
        # else build final result from result, args, outmask, and
        # inoutmask. Typically it's just result, unless you specify
        # out/inout parameters in the prototype.
        return args

    _HandlerRoutine = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

    _kernel32.SetConsoleCtrlHandler.errcheck = _check_bool
    _kernel32.SetConsoleCtrlHandler.argtypes = (_HandlerRoutine,
                                                wintypes.BOOL)

    _console_ctrl_handlers = {}

    def set_console_ctrl_handler(handler):
        if handler not in _console_ctrl_handlers:
            h = _HandlerRoutine(handler)
            _kernel32.SetConsoleCtrlHandler(h, True)
            _console_ctrl_handlers[handler] = h

    signals_reverse[signal.CTRL_C_EVENT] = 'CTRL_C_EVENT'
    signals_reverse[signal.CTRL_BREAK_EVENT] = 'CTRL_BREAK_EVENT'


def signal_receiver(sig, frame):
    [t(sig, frame) for t in sig_catchers]


def handler(sig):
    signal_receiver(sig, None)
    return 1


def signal_all_setup(func=None):
    global is_set_up, sig_catchers

    if func is not None:
        sig_catchers.append(func)

    if not is_set_up:
        is_set_up = True
        if os.name == 'nt':
            set_console_ctrl_handler(handler)
        for i in [
            'SIGINT', 'SIGHUP', 'SIGTERM', 'SIGUSR1', 'SIGUSR2', 'SIGFPE',
            'SIGQUIT', 'SIGSEGV', 'SIGXCPU', 'SIGBUS', 'SIGKILL', 'SIGILL', 'SIGBREAK'
        ]:
            if hasattr(signal, i):
                try:
                    signal.signal(getattr(signal, i), signal_receiver)
                    signals_reverse[getattr(signal, i)] = i
                    # print "set "+i
                except ValueError:
                    # print "error with "+i
                    pass