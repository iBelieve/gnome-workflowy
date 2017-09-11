import os
import json
from gi.repository import GObject
from . import api
from .utils import do_async


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

        if os.path.exists(self.session_file):
            with open(self.session_file) as f:
                self.session_id = f.read()

            if os.path.exists(self.data_file):
                with open(self.data_file) as f:
                    self.data = json.load(f)

            self.refresh()

    def sign_in(self, email, password):
        def background_task():
            session_id = api.sign_in(email, password)
            data = api.get_data(session_id)
            return session_id, data

        def on_done(session_id, data):
            with open(self.session_file, 'w') as f:
                f.write(session_id)
            with open(self.data_file, 'w') as f:
                json.dump(data, f)

            self.session_id = session_id
            self.data = data
            self.emit('notify::is_signed_in', self.is_signed_in)
            self.emit('signed_in')

        def on_error(error):
            self.emit('signin_error', error)

        do_async(background_task, on_done, on_error)

    def sign_out(self):
        self.session_id = None
        self.data = None
        self.emit('notify::is_signed_in')

    def refresh(self):
        def background_task():
            return api.get_data(self.session_id)

        def on_done(data):
            with open(self.data_file, 'w') as f:
                json.dump(data, f)

            self.data = data

        def on_error(error):
            self.emit('data_error', error)

        do_async(background_task, on_done, on_error)

    @GObject.Property
    def is_signed_in(self):
        return self.session_id is not None
