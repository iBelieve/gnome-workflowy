from gi.repository import Gtk, GLib, GObject
from .exceptions import LoginFailedException


class SignIn(Gtk.Bin):
    def __init__(self, workflowy):
        super().__init__()
        self.workflowy = workflowy

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/io/mspencer/Workflowy/ui/signin.ui')
        builder.connect_signals(self)

        self.add(builder.get_object("widget"))

        self.signin_button = builder.get_object("signin_button")
        self.email_entry = builder.get_object("email_entry")
        self.password_entry = builder.get_object("password_entry")
        self.signin_button_label = builder.get_object("signin_button_label")
        self.signin_button_spinner = builder.get_object("signin_button_spinner")
        self.error_label = builder.get_object("error_label")

    def connect_signals(self):
        self.workflowy.connect('signin_error', self.on_error)

    # State management

    def set_state_ready(self):
        self.signin_button.props.sensitive = True
        self.email_entry.props.sensitive = True
        self.password_entry.props.sensitive = True
        self.signin_button_label.props.label = "Sign in"
        self.signin_button_spinner.hide()
        self.email_entry.grab_focus()

    def set_state_busy(self):
        self.signin_button.props.sensitive = False
        self.email_entry.props.sensitive = False
        self.password_entry.props.sensitive = False
        self.signin_button_label.props.label = "Signing in..."
        self.signin_button_spinner.show()

    # Signal handlers

    def on_email_entry_activate(self, entry):
        self.password_entry.grab_focus()

    def on_password_entry_activate(self, entry):
        if self.signin_button.props.sensitive:
            self.signin_button.activate()

    def on_entry_changed(self, entry):
        has_valid_email = '@' in self.email_entry.props.text
        has_valid_password = len(self.password_entry.props.text) > 0
        self.signin_button.props.sensitive = has_valid_email and has_valid_password

    def on_signin_clicked(self, button):
        email = self.email_entry.props.text
        password = self.password_entry.props.text

        self.set_state_busy()
        self.workflowy.sign_in(email, password)

    def on_error(self, workflowy, error):
        print(error)
        if isinstance(error, LoginFailedException):
            self.error_label.props.label = "Wrong username or password"
        else:
            self.error_label.props.label = "Unable to sign in"
        self.error_label.show()
        self.set_state_ready()
