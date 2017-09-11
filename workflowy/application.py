import os
from gi.repository import GLib, Gtk
from .workflowy import Workflowy
from .window import Window


class Application(Gtk.Application):
    def __init__(self, version):
        super().__init__(application_id='io.mspencer.Workflowy')

        self.version = version
        self.datadir = os.path.join(GLib.get_user_data_dir(), 'gnome-workflowy')

        GLib.set_application_name('Workflowy')
        GLib.set_prgname('workflowy')

    # Signal handlers

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.workflowy = Workflowy(self.datadir)

    def do_activate(self):
        Gtk.Application.do_activate(self)
        window = Window(self, self.workflowy)
        window.show_all()
