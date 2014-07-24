#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
import os
import sys
from Login import LoginWindow
from lib.Constructor import Gtk
from lib.DBAdmin import Querys

class ProfilesSwitch_Window():
    def __init__(self, parent, user, callbacks=[]):
        self.parent = parent
        self.parent.hide()

        self.callbacks = callbacks
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_resizable(False)
        self.window.set_title('Switch Profile')
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        self.window.add(self.create_frame(user))
        self.window.show()

    def create_frame(self, user):
        vbox = Gtk().make_vbox()

        hbox = Gtk().make_hbox()
        frame = Gtk().make_frame({'name':'Profiles', 'border':5})
        vbox_frame = Gtk().make_vbox({'border':3})
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        cell = gtk.CellRendererText()
        combo_profiles = gtk.ComboBox(model)
        combo_profiles.show()
        combo_profiles.pack_start(cell, True)
        combo_profiles.add_attribute(cell, 'text', 1)
        vbox_frame.pack_start(combo_profiles, True, True, 5)
        frame.add(vbox_frame)

        button_box = Gtk().make_vbox({'border':3})
        button_switch = Gtk().make_button(self.switch_profile, None)
        button_switch.set_tooltip_text('Switch profile')
        image_switch = Gtk().make_image({'stock':gtk.STOCK_SAVE})
        button_switch.add(image_switch)

        button_cancel = Gtk().make_button(self.close_window, None)
        button_cancel.set_tooltip_text('Cancel')
        image_cancel = Gtk().make_image({'stock':gtk.STOCK_CANCEL})
        button_cancel.add(image_cancel)
        button_box.pack_start(button_switch, True, True, 0)
        button_box.pack_start(button_cancel, True, True, 0)

        hbox.pack_start(frame, False, False, 2)
        hbox.pack_start(button_box, False, False, 0)

        vbox.pack_start(hbox, False, True, 0)
        
        self.load_profiles(combo_profiles, user)
        
        self.combo_profiles = combo_profiles
        return vbox

    def load_profiles(self, widget, user):
        profiles = Querys().all_table('profiles', True)
        model = widget.get_model()
        for i in profiles:
            model.append((profiles[i]['id'],
                          profiles[i]['profile']))
        tree_iter = model.get_iter_first()
        while tree_iter:
            profile = model.get_value(tree_iter, 1)
            if profile == user:
                widget.set_active_iter(tree_iter)
                break
            tree_iter = model.iter_next(tree_iter)        
            
    def get_form_values(self):
        model = self.combo_profiles.get_model()
        active = self.combo_profiles.get_active_iter()
        profile = {'id':model.get_value(active, 0),
                   'profile':model.get_value(active, 1)}
        return profile

    def switch_profile(self, widget):
        profile = self.get_form_values()
        self.window.hide()
        self.window.destroy()
        LoginWindow(self.parent, profile['profile'], self.callbacks)

    def close_window(self, widget=None, event=None):
        self.window.hide()
        self.window.destroy()
        self.parent.show()
        self.parent.set_sensitive(True)
        
