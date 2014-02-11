from callback import CallbackEvent
from utils import display_alert
import traceback

def report_exception(client_name, e):
    # display alert on main thread
    exception_name = str(e)
    traceback_info = traceback.format_exc()
    CallbackEvent.post(lambda: display_alert("Unexpected %s request error" % client_name,
                                             traceback_info,
                                             exception_name))