import sys
import traceback
from core import my_log
log = my_log.Log(__name__).getlog()


def log_except_hook(*exc_info):
    text = "".join(traceback.format_exception(*exc_info))

    log.critical("Unhandled exception: %s", text)


sys.excepthook = log_except_hook
started_thread_number = None
started_thread_name = None
now_file = None
df = None
