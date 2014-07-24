#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gtk
import gobject
import os
from lib.Constructor import Gtk
from lib.Path import APP_NAME, THEME_PATH, CONF_FILE, _get_configFile

class PreferencesWindow():
    def __init__(self, parent=None, callbacks=[]):
        self.parent = parent
        self.parent.set_sensitive(False)
        
        self.callbacks = callbacks
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_icon_from_file(os.path.join(THEME_PATH, 'package.png'))
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_resizable(False)
        self.window.set_screen(self.parent.get_screen())
        self.window.set_title('%s - Preferences' %(APP_NAME))
        self.window.set_transient_for(self.parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        self.window.add(self.create_frame())
        self.window.show()

        self.load_preferences()

    def create_frame(self):
        vbox = Gtk().make_vbox()

        frame = Gtk().make_frame({'border':7})
        hbox_frame = Gtk().make_hbox()

        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.save_preferences},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})
        
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(buttons, False, False, 0)

        image = Gtk().make_image({'stock':gtk.STOCK_PREFERENCES,
                                  'size':gtk.ICON_SIZE_DIALOG})
        
        hbox_frame.pack_start(image, True, True, 25)

        vbox_lab = Gtk().make_vbox()
        label_names = ['Tab Position']
        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_lab.pack_start(label_dict[i], True, True, 2) for i in label_names]
        hbox_frame.pack_start(vbox_lab, True, False, 3)

        vbox_entry = Gtk().make_vbox()
        entrys = ['tabpos']

        tabpos_opt = ['left', 'right', 'bottom', 'top']
        
        cell = gtk.CellRendererText()
        combo_tabpos = gtk.ComboBox(gtk.ListStore(gobject.TYPE_STRING,
                                                  gobject.TYPE_STRING))
        combo_tabpos.pack_start(cell, True)
        combo_tabpos.add_attribute(cell, "text", 1)
        combo_tabpos.show()

        self.load_combo(combo_tabpos, tabpos_opt)

        combo_dict = {'tabpos':combo_tabpos}
        [vbox_entry.pack_start(combo_dict[i], True, False, 2) for i in entrys]

        hbox_frame.pack_start(vbox_entry, True, True, 3)
        
        frame.add(hbox_frame)

        self.combo_dict = combo_dict
        return vbox

    def load_combo(self, widget, values):
        model = widget.get_model()
        counter = 0
        for i in values:
            model.append((counter, i))
            counter += 1
        widget.set_active(0)

    def load_preferences(self, widget=None):
        configFile = _get_configFile(CONF_FILE)
        for i in self.combo_dict:
            model = self.combo_dict[i].get_model()
            tree_iter = model.get_iter_first()
            while tree_iter:
                type_available = model.get_value(tree_iter, 1)
                if configFile[i] == type_available:
                    self.combo_dict[i].set_active_iter(tree_iter)
                    break
                tree_iter = model.iter_next(tree_iter)

    def save_preferences(self, widget=None):
        new_preferences = {}
        for i in self.combo_dict:
            model = self.combo_dict[i].get_model()
            active = self.combo_dict[i].get_active_iter()
            new_preferences[i] = model.get_value(active, 1)

        configFile = _get_configFile(CONF_FILE)
        configFile.update(new_preferences)
        configFile.write()
        [i('[Info] Preferences saved.') for i in self.callbacks]
        self.close_window()

    def close_window(self, widget=None, event=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
