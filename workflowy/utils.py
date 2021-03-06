import calendar
import threading
from datetime import date, timedelta
from inspect import signature
from gi.repository import GLib
from html.parser import HTMLParser


WEEK = [calendar.SUNDAY, calendar.MONDAY, calendar.TUESDAY, calendar.WEDNESDAY,
        calendar.THURSDAY, calendar.FRIDAY, calendar.SATURDAY]
TODAY = date.today()


def day_this_week(weekday):
    today = date.today()
    return today - timedelta(days=WEEK.index(today.weekday()) - WEEK.index(weekday))


def do_async(target, on_done=None, on_error=None):
    def background_task():
        try:
            res = target()
            if on_done is not None:
                sig = signature(on_done)
                if len(sig.parameters) == 0 and res is None:
                    GLib.idle_add(on_done)
                elif isinstance(res, tuple):
                    GLib.idle_add(on_done, *res)
                else:
                    GLib.idle_add(on_done, res)
        except Exception as ex:
            if on_error is not None:
                GLib.idle_add(on_error, ex)

    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
