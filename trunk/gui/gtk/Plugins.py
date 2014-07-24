#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
import os
import pango
import sys
from lib.Constructor import Gtk
from lib.Path import APP_PATH, APP_NAME, THEME_PATH

class PluginsWindow():
    def __init__(self, parent, user):
        self.parent = parent
        self.parent.set_sensitive(False)

        self.user = user
        self.session = os.environ['LOGNAME']

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_icon_from_file(os.path.join(THEME_PATH, 'package.png'))
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_resizable(False)
        self.window.set_screen(parent.get_screen())
        self.window.set_size_request(500, 500)
        self.window.set_title('%s - Plugins' %(APP_NAME))
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        if gtk.gtk_version >= (2, 14):
            self.parent.set_parent_window(self.window.get_window())

        self.plugins_active = []

        self.window.add(self.create_frame())
        self.window.show()

    def create_frame(self):
        vbox = Gtk().make_vbox()
        frame = Gtk().make_frame({'name':'Plugin List','border':7})

        button_list = [{'stock':gtk.STOCK_ADD,'cmd':self.close_window},
                       {'stock':gtk.STOCK_CLOSE,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})
        
        vbox.pack_start(frame, True, True, 2)
        vbox.pack_start(buttons, False, False, 2)

        hbox_frame = Gtk().make_hbox()
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_border_width(10)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_vbox = Gtk().make_vbox()
        scroll_vbox.pack_start(scrolledwindow, True)
        
        model = gtk.TreeStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING,
                              gobject.TYPE_STRING)
        model.set_sort_column_id(1, gtk.SORT_ASCENDING)
        
        treeview = gtk.TreeView(model)
        treeview.columns_autosize()
        treeview.connect('button_press_event', self.list_right_button)
        treeview.set_reorderable(True)
        cell = gtk.CellRendererText()
        cell_toggle = gtk.CellRendererToggle()
        cell_toggle.set_property('activatable', True)
        cell_toggle.connect('toggled', self.cell_toggled_cb, model)
        column_select = gtk.TreeViewColumn('Active', cell_toggle)
        column_select.add_attribute(cell_toggle, 'active', 0)
        column_description = gtk.TreeViewColumn('Description', cell)
        column_description.set_attributes(cell, text=1)
        column_description.set_sort_column_id(1)
        column_description.set_sort_indicator(True)
        treeview.append_column(column_select)
        treeview.append_column(column_description)
        treeview.show()
        scrolledwindow.add(treeview)
        scrolledwindow.show()

        hbox_frame.pack_start(scroll_vbox, True, True, 2)
        frame.add(hbox_frame)

        self.treeview = treeview
        return vbox

    def cell_toggled_cb(self, cell, path, model):
        model[path][0] = not model[path][0]
        if model[path][0]:
            self.plugins_active.append(model[path][1])
        else:
            if self.plugins_active.count(model[path][1]):
                self.plugins_active.remove(model[path][1])

    def list_right_button(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x,y)
            if pthinfo is not None:
                path,col,cellx,celly = pthinfo
                selection = treeview.get_selection()
                tree_model, tree_iter = selection.get_selected()
                treeview.grab_focus()
                treeview.set_cursor(path,col,0)
                if tree_iter:
                    plugin_name = tree_model.get_value(tree_iter, 1)
                    menu = self.list_menu_popup(plugin)
                    menu.popup(None, None, None, event.button, event.time)
            return 1

    def list_menu_popup(self, plugin_name):
        menu = gtk.Menu()
        # Generator file_menu
        edit = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        # edit.connect('activate', self.window_server_modify,
        #              'single', [str(server_id)])
        edit.show()
        remove = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        # remove.connect('activate', self.confirm_server_remove, server_id)
        remove.show()
        menu.append(plugins)
        menu.append(separator_opt)
        menu.append(edit)
        menu.append(remove)
        return menu

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
