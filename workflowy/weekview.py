import calendar
from gi.repository import Gtk
from .utils import WEEK, TODAY, day_this_week


class WeekView(Gtk.Grid):
    def __init__(self):
        super().__init__(margin=16, column_spacing=16, row_spacing=16,
                         column_homogeneous=True, row_homogeneous=True)

        for index, day in enumerate(WEEK):
            day_view = DayView(day)
            col = index % 4
            row = index // 4
            self.attach(day_view, col, row, 1, 1)

        day_view = DayView(day=None)
        self.attach(day_view, 3, 1, 1, 1)


class DayView(Gtk.Bin):
    label: Gtk.Label
    list: Gtk.ListBox

    def __init__(self, day):
        super().__init__()
        self.day = day

        self.setup_ui()

        if day is not None:
            self.date = day_this_week(day)

            self.label.props.label = f"{self.date.day} {calendar.day_name[day]}"

            if self.date < TODAY:
                self.props.opacity = 0.5
        else:
            self.label.props.label = 'Unscheduled'

    def setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/io/mspencer/Workflowy/ui/day.ui')

        self.label = builder.get_object('day_label')
        self.list = builder.get_object('list')
        self.add(builder.get_object('widget'))

