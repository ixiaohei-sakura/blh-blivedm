import ctypes
import inspect
import threading


class ThreadForceExit(SystemExit):
    pass


def __async_raise(tid, exctype):
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread, exception=ThreadForceExit):
    try:
        __async_raise(thread.ident, exception)
    except TypeError:
        return False
    except ValueError:
        return False
    except SystemError:
        return False
    else:
        return True


class Thread(threading.Thread):
    def __init__(self, group=None, name="Base", daemon=True, target=None, args=()):
        super(Thread, self).__init__(group=group, name=name, daemon=daemon, target=target, args=args)

    def force_stop(self):
        stop_thread(self)
