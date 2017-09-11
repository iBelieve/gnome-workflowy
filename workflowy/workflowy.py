import calendar
import os
import json
import re
from typing import List
from collections import defaultdict
from datetime import date
from dateutil.parser import parse
from gi.repository import GObject
from . import api
from .utils import do_async, strip_tags


class Workflowy(GObject.Object):
    __gsignals__ = {
        'signed_in': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'signed_out': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'signin_error': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'data_error': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }

    session_id = None
    data = GObject.Property(type=object)

    def __init__(self, datadir):
        super().__init__()
        self.datadir = datadir
        self.session_file = os.path.join(self.datadir, 'session_id')
        self.data_file = os.path.join(self.datadir, 'data.json')

        self.planner = Planner(self)

        if os.path.exists(self.session_file):
            with open(self.session_file) as f:
                self.session_id = f.read()

            if os.path.exists(self.data_file):
                with open(self.data_file) as f:
                    self.set_data(json.load(f), save=False)

            self.refresh()

    def set_data(self, data, save=True):
        if save:
            with open(self.data_file, 'w') as f:
                json.dump(data, f)

        self.data = [Node(**d) for d in data]

    def sign_in(self, email, password):
        def background_task():
            session_id = api.sign_in(email, password)
            data = api.get_data(session_id)
            return session_id, data

        def on_done(session_id, data):
            with open(self.session_file, 'w') as f:
                f.write(session_id)
            self.session_id = session_id
            self.set_data(data)
            self.emit('notify::is_signed_in', self.is_signed_in)
            self.emit('signed_in')

        do_async(background_task, on_done,
                 lambda error: self.emit('signin_error', error))

    def sign_out(self):
        self.session_id = None
        self.data = None
        self.emit('notify::is_signed_in')

    def refresh(self):
        do_async(lambda: api.get_data(self.session_id),
                 lambda data: self.set_data(data),
                 lambda error: self.emit('data_error', error))

    @GObject.Property
    def is_signed_in(self):
        return self.session_id is not None


class Node:
    def __init__(self, id, nm, no=None, ch=None, **kwargs):
        self.id = id
        self.name = nm
        self.note = no
        self.children = [Node(**d) for d in ch] if ch else list()

    @property
    def stripped_name(self):
        return strip_tags(self.name)

    def __repr__(self):
        return self.stripped_name


class Planner(GObject.Object):
    __gsignals__ = {
        'events_changed': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    months: List[Node] = list()

    def __init__(self, workflowy):
        super().__init__()
        self.workflowy = workflowy
        self.workflowy.connect('notify::data', self.on_data_changed)
        if workflowy.data is not None:
            self.on_data_changed(workflowy, workflowy.data)

    def on_data_changed(self, workflowy, paramspec):
        self.months = next(item for item in workflowy.data if item.stripped_name == "Planner").children
        self.emit('events_changed')

    @property
    def unscheduled_tasks(self):
        return next(item for item in self.months if item.stripped_name == 'Unscheduled').children

    def events_for_month(self, month_name):
        events = defaultdict(lambda: list())
        month_names = [previous_month(month_name), month_name, next_month(month_name)]
        months = [month for month in self.months if month.stripped_name in month_names]
        weeks = [week for month in months for week in month.children]

        for week in weeks:
            week_start, week_end = parse_week(week.name)
            if week_start is None:
                continue
            if week_start.strftime('%B') != month_name and week_end.strftime('%B') != month_name:
                continue

            for day in week.children:
                date = parse_day(day.stripped_name, week_start, week_end)
                if date.strftime('%B') != month_name:
                    continue

                events[date].extend(day.children)

        return events


def previous_month(month):
    index = list(calendar.month_name).index(month)
    if index > 0:
        return calendar.month_name[index - 1]


def next_month(month):
    index = list(calendar.month_name).index(month)
    if index < len(calendar.month_name) - 1:
        return calendar.month_name[index + 1]


def parse_week(week: str):
    splits = re.split(r'\s+-\s+', week)
    if len(splits) != 2:
        return None, None

    [week_start, week_end] = splits

    week_start = parse(week_start)

    if week_end[0].isdigit():
        week_end = week_start.strftime('%B') + ' ' + week_end
    week_end = parse(week_end)

    return week_start, week_end


def parse_day(day: str, week_start: date, week_end: date):
    [day, weekday] = day.split(' ')
    day = int(day)

    if day >= week_start.day:
        return date(week_start.year, week_start.month, day)
    elif day <= week_end.day:
        return date(week_end.year, week_end.month, day)
    else:
        raise Exception(f"Day outside of week: {week_start} - {week_end}: {day}")
