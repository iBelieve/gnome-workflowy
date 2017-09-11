from gi.repository import Gtk
from .signin import SignIn
from .weekview import WeekView
from .workflowy import Workflowy


class Window(Gtk.ApplicationWindow):
    def __init__(self, application, workflowy: Workflowy):
        super().__init__(application=application,
                         title='Workflowy',
                         icon_name='io.mspencer.Workflowy')
        self.app = application
        self.workflowy = workflowy

        self.setup_ui()
        self.connect_signals()

    # UI Setup

    def connect_signals(self):
        self.workflowy.connect('notify::is_signed_in', self.on_signed_in_changed)

        self.on_signed_in_changed(self.workflowy, self.workflowy.is_signed_in)

    def setup_ui(self):
        self.main_stack = Gtk.Stack()
        self.add(self.main_stack)

        self.setup_signin()
        self.setup_weekview()
        self.setup_titlebar()

    def setup_signin(self):
        self.signin = SignIn(self.workflowy)
        self.signin.show()
        self.main_stack.add(self.signin)

    def setup_weekview(self):
        self.weekview = WeekView()
        self.weekview.show()
        self.main_stack.add(self.weekview)

    def setup_titlebar(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/io/mspencer/Workflowy/ui/titlebar.ui')
        builder.connect_signals(self)

        self.main_titlebar = builder.get_object('widget')

    # Signal handlers

    def on_signed_in_changed(self, workflowy, is_signed_in):
        print(is_signed_in)
        if is_signed_in:
            self.set_titlebar(self.main_titlebar)
            self.main_stack.set_visible_child(self.weekview)
        else:
            titlebar = Gtk.HeaderBar(title='Sign In', show_close_button=True)
            self.set_titlebar(titlebar)
            self.main_stack.set_visible_child(self.signin)
