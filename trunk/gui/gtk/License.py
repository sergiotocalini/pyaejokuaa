#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
import os
import sys
from lib.Constructor import Gtk
from lib.Path import APP_NAME, APP_PATH

class LicenseWindow():
    def __init__(self, parent=None):
        self.parent = parent
        self.parent.set_sensitive(False)
        self.parent.hide()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.set_screen(parent.get_screen())
        self.window.set_size_request(500, 450)
        self.window.set_title('%s - License' %(APP_NAME))
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        
        vbox = gtk.VBox()
        vbox.show()
        frame = gtk.Frame()
        frame.set_border_width(3)
        frame.show()
        frame.add(self.load_license())

        button_list = [{'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})

        vbox.pack_start(frame, True, True, 2)
        vbox.pack_start(buttons, False, False, 0)

        self.window.add(vbox)
        self.window.show()

    def load_license(self):
        view = gtk.TextView()
        view.set_editable(False)
        buffer_text = view.get_buffer()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(view)

        license_text = open(os.path.join(APP_PATH, 'doc/LICENSE'), 'r').read()
        
        iter_number = buffer_text.get_iter_at_offset(0)
        buffer_text.insert(iter_number, license_text)

        scrolled_window.show_all()
        return scrolled_window
        
    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
        self.parent.show()
