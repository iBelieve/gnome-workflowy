import calendar
from gi.repository import Gtk
from .utils import WEEK, TODAY, day_this_week
from typing import List


class WeekView(Gtk.Grid):
    day_views = []

    def __init__(self, planner):
        super().__init__(margin=16, column_spacing=16, row_spacing=16,
                         column_homogeneous=True, row_homogeneous=True)
        for index, day in enumerate(WEEK):
            day_view = DayView(day)
            col = index % 4
            row = index // 4
            self.day_views.append(day_view)
            self.attach(day_view, col, row, 1, 1)

        self.unscheduled_view = DayView(day=None)
        self.attach(self.unscheduled_view, 3, 1, 1, 1)

        planner.connect('events_changed', self.update_events)
        self.update_events(planner)

    def update_events(self, planner):
        events = planner.events_for_month(TODAY.strftime('%B'))

        for day_view in self.day_views:
            day_view.set_events(events[day_view.date])
        self.unscheduled_view.set_events(planner.unscheduled_tasks)


class DayView(Gtk.Bin):
    label: Gtk.Label
    listbox: Gtk.ListBox
    rows: List[Gtk.ListBoxRow]

    def __init__(self, day):
        super().__init__()
        self.day = day
        self.rows = list()

        self.setup_ui()
        self.set_day(day)

    def set_day(self, day):
        if day is not None:
            self.date = day_this_week(day)

            label = f"{self.date.day} {calendar.day_name[day]}"
            if self.date == TODAY:
                self.label.set_markup(f'<b>{label}</b>')
            else:
                self.label.props.label = label

            if self.date < TODAY:
                self.props.opacity = 0.6
        else:
            self.label.props.label = 'Unscheduled'

    def set_events(self, events):
        for row in self.rows:
            self.listbox.remove(row)

        for event in events:
            row = TaskListRow(event)
            row.show_all()
            self.rows.append(row)
            self.listbox.add(row)

    def setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/io/mspencer/Workflowy/ui/day.ui')

        self.label = builder.get_object('day_label')
        self.listbox = builder.get_object('list')
        self.add(builder.get_object('widget'))


class TaskListRow(Gtk.ListBoxRow):
    def __init__(self, task):
        super().__init__(selectable=False, activatable=True)
        self.task = task

        self.row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                           margin_left=8, margin_right=8,
                           margin_top=4, margin_bottom=4)
        self.add(self.row)

        self.checkbox = Gtk.CheckButton(active=task.is_completed, valign=Gtk.Align.CENTER)
        self.checkbox.connect('toggled', self.on_toggled)
        self.row.add(self.checkbox)

        self.label = Gtk.Label(xalign=0, wrap=True)
        self.row.add(self.label)

        self.set_completed(task.is_completed)

    def on_toggled(self, checkbox):
        self.set_completed(checkbox.props.active)

    def set_completed(self, completed):
        self.label.props.opacity = 0.5 if completed else 1.0
        self.label.set_markup(f'<s>{self.task.name}</s>' if completed else self.task.name)
