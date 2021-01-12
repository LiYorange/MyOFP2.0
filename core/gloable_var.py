import cores
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
# def setter(var, value=None):
#     if value is not None:
#         try:
#             var = value
#         except Exception as e:
#             log.error(e)
#
#
# def getter(var, default=None):
#     try:
#         return var
#     except Exception as e:
#         log.error(e)
#         return default
#
#
# if __name__ == '__main__':
#     df = None
#     s = input()
#     df = cores.read_csv("../db/60004036_20200930（外罗）.csv")
#     x = input()
#     df = None
#     y = input()
