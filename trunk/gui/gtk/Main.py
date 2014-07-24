#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
try:
    import gobject
    import gtk
    import pango
    from datetime import datetime
except:
    print ('''You need to install the following libraries:
          pygtk, gobject, pango, datatime''')
    sys.exit(1)

import os
import sys
from About import AboutWindow
from Login import LoginWindow
from Plugins import PluginsWindow
from Preferences import PreferencesWindow
from ProfilesAdd import ProfilesAddWindow
from ProfilesSwitch import ProfilesSwitch_Window
from ServerAdd import ServerAddWindow
from ServerExport import ServerExportWindow
from ServerImport import ServerImportWindow
from ServerModify import ServerModifyWindow
from lib.Constructor import Gtk
from lib.Controller import *
from lib.DBAdmin import Querys
from lib.Path import APP_NAME, THEME_PATH, CONF_FILE, _get_configFile
from lib.PluginManager import *
from lib.ThreadAgent import Agent

class MainWindow():
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_application)
        self.window.maximize()
        self.window.set_icon_from_file(os.path.join(THEME_PATH, 'package.png'))
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title('%s - Main' %(APP_NAME))

        self.register_stock_icons()        
        self.servers_active = []

        self.window.add(self.create_summary())
        self._load_preferences()
        self.window_login()

    def _set_profile(self, profile, password):
        self._profile = profile
        self._password = password

        self.window.show()
        self.load_machines()

    def _load_preferences(self, widget=None):
        configFile = _get_configFile(CONF_FILE)
        
        if configFile['tabpos'] == 'top':
            self.notebook.set_tab_pos(gtk.POS_TOP)
        elif configFile['tabpos'] == 'bottom':
            self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        elif configFile['tabpos'] == 'right':
            self.notebook.set_tab_pos(gtk.POS_RIGHT)
        elif configFile['tabpos'] == 'left':
            self.notebook.set_tab_pos(gtk.POS_LEFT)

    def register_stock_icons(self):
        items = [('gtk-about','About',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-export','Export',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-import','Import',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-import-sql','SQL',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-import-srv','Server',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-plugins','Plugins',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-preferences','Preferences',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-profile','Profile',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-profile-edit','Profile',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-profile-switch','Switch',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-quit','Quit',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-select-all','Select All',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-server','Server',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-server-mod','Selected',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-server-mod-all','All',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-unselect','Unselect All',gtk.gdk.CONTROL_MASK,0,'gtk20'),
                 ('gtk-website', 'Homepage',gtk.gdk.CONTROL_MASK,0,'gtk20')]
        
        alias = [('gtk-about',gtk.STOCK_ABOUT),
                 ('gtk-export',gtk.STOCK_SAVE_AS),
                 ('gtk-import',gtk.STOCK_SAVE),
                 ('gtk-import-sql',gtk.STOCK_OPEN),
                 ('gtk-import-srv',gtk.STOCK_OPEN),
                 ('gtk-plugins',gtk.STOCK_EXECUTE),
                 ('gtk-preferences',gtk.STOCK_PREFERENCES),
                 ('gtk-profile',gtk.STOCK_DIALOG_AUTHENTICATION),
                 ('gtk-profile-edit',gtk.STOCK_DIALOG_AUTHENTICATION),
                 ('gtk-profile-switch',gtk.STOCK_CONVERT),
                 ('gtk-quit',gtk.STOCK_QUIT),
                 ('gtk-select-all',gtk.STOCK_INDEX),
                 ('gtk-server',gtk.STOCK_NETWORK),
                 ('gtk-server-mod',gtk.STOCK_EDIT),
                 ('gtk-server-mod-all',gtk.STOCK_EDIT),
                 ('gtk-unselect',gtk.STOCK_INDEX),
                 ('gtk-website',gtk.STOCK_HOME)]

        gtk.stock_add(items)

        factory = gtk.IconFactory()
        factory.add_default()
        for new_stock, name_stock in alias:
            icon_set = gtk.icon_factory_lookup_default(name_stock)
            factory.add(new_stock, icon_set)

    def notebook_delete(self, widget=None, notebook=None):
        if not notebook:
            notebook = self.notebook
        page = notebook.get_current_page()
        notebook.remove_page(page)
        notebook.queue_draw_area(1,1,1,1)

    def create_summary(self):
        vbox = Gtk().make_vbox({'spacing':2})

        notebook = Gtk().make_notebook()

        options = {'name':'Summary', 'stock':gtk.STOCK_HOME}
        page, vbox_note = Gtk().make_notebook_tab(notebook, options)
        vbox_note.pack_start(self.create_frame_summary(), True, True, 0)
        notebook.set_current_page(page)

        vbox.pack_start(self.create_menubar(), False, True, 1)
        vbox.pack_start(self.create_toolbar(), False, False, 1)
        vbox.pack_start(notebook, True, True, 1)
        vbox.pack_start(self.create_statusbar(), False, True, 1)
        
        self.notebook = notebook
        return vbox

    def create_menubar(self):
        menu_accel = gtk.AccelGroup()
        self.window.add_accel_group(menu_accel)
        
        menu_bar = gtk.MenuBar()
        menu_bar.append(self._gen_menu_file(menu_accel))
        menu_bar.append(self._gen_menu_edit(menu_accel))
        menu_bar.append(self._gen_menu_option(menu_accel))
        menu_bar.append(self._gen_menu_help(menu_accel))
        menu_bar.show()
        return menu_bar

    def _gen_menu_file(self, accel_group):
        separator1 = gtk.SeparatorMenuItem()
        separator1.show()
        separator2 = gtk.SeparatorMenuItem()
        separator2.show()

        swi_key, swi_mod = gtk.accelerator_parse('<Control>S')
        switch_pro = gtk.ImageMenuItem('gtk-profile-switch')
        switch_pro.add_accelerator('activate', accel_group, swi_key,
                                   swi_mod, gtk.ACCEL_VISIBLE)
        switch_pro.set_tooltip_text('Switch profile.')
        switch_pro.connect('activate', self.window_profiles_switch)
        switch_pro.show()

        separator3 = gtk.SeparatorMenuItem()
        separator3.show()

        quit_key, quit_mod = gtk.accelerator_parse('<Control>Q')
        item_quit = gtk.ImageMenuItem('gtk-quit', gtk.ICON_SIZE_MENU)
        item_quit.add_accelerator('activate', accel_group, quit_key,
                                  quit_mod, gtk.ACCEL_VISIBLE)
        item_quit.connect('activate', self.close_application)
        item_quit.show()
        
        menu = gtk.Menu()
        menu.append(self._gen_file_submenu_new(accel_group))
        menu.append(separator1)
        menu.append(self._gen_file_submenu_export(accel_group))
        menu.append(self._gen_file_submenu_import(accel_group))
        menu.append(separator2)
        menu.append(switch_pro)
        menu.append(separator3)
        menu.append(item_quit)
        item_file = gtk.MenuItem('File')
        item_file.set_submenu(menu)
        item_file.set_right_justified(True)
        item_file.show()
        return item_file

    def _gen_file_submenu_new(self, accel_group):
        prof_key, prof_mod = gtk.accelerator_parse('<Control><Shift>P')
        new_pro = gtk.ImageMenuItem('gtk-profile', gtk.ICON_SIZE_MENU)
        new_pro.add_accelerator('activate', accel_group, prof_key,
                                prof_mod, gtk.ACCEL_VISIBLE)
        new_pro.set_tooltip_text('New profile')
        new_pro.connect('activate', self.window_profiles_add)
        new_pro.show()
        new_key, new_mod = gtk.accelerator_parse('<Control><Shift>N')
        new_server = gtk.ImageMenuItem('gtk-server')
        new_server.add_accelerator('activate', accel_group, new_key,
                                   new_mod, gtk.ACCEL_VISIBLE)
        new_server.set_tooltip_text('New server')
        new_server.connect('activate', self.window_server_add)
        new_server.show()

        menu = gtk.Menu()
        menu.append(new_pro)
        menu.append(new_server)
        item_server = gtk.ImageMenuItem(gtk.STOCK_NEW)
        item_server.set_submenu(menu)
        item_server.set_right_justified(True)
        item_server.show()
        return item_server

    def _gen_file_submenu_import(self, accel_group):
        imp_key, imp_mod = gtk.accelerator_parse('<Control><Shift>I')
        import_server = gtk.ImageMenuItem('gtk-server', gtk.ICON_SIZE_MENU)
        import_server.add_accelerator('activate', accel_group, imp_key,
                                      imp_mod, gtk.ACCEL_VISIBLE)
        import_server.connect('activate', self.window_server_import)
        import_server.show()
        separator = gtk.SeparatorMenuItem()
        separator.show()

        menu = gtk.Menu()
        menu.append(import_server)
        # menu.append(separator)
        item_server = gtk.ImageMenuItem('gtk-import')
        item_server.set_submenu(menu)
        item_server.set_right_justified(True)
        item_server.show()
        return item_server

    def _gen_file_submenu_export(self, accel_group):
        imp_key, imp_mod = gtk.accelerator_parse('<Control><Shift>E')
        import_server = gtk.ImageMenuItem('gtk-server', gtk.ICON_SIZE_MENU)
        import_server.add_accelerator('activate', accel_group, imp_key,
                                      imp_mod, gtk.ACCEL_VISIBLE)
        import_server.connect('activate', self.window_server_export)
        import_server.show()
        separator = gtk.SeparatorMenuItem()
        separator.show()

        menu = gtk.Menu()
        menu.append(import_server)
        # menu.append(separator)
        item_server = gtk.ImageMenuItem('gtk-export')
        item_server.set_submenu(menu)
        item_server.set_right_justified(True)
        item_server.show()
        return item_server

    def _gen_menu_edit(self, accel_group):
        edit_key, edit_mod = gtk.accelerator_parse('F3')
        edit_pro = gtk.ImageMenuItem('gtk-profile-edit')
        edit_pro.add_accelerator('activate', accel_group, edit_key,
                                 edit_mod, gtk.ACCEL_VISIBLE)
        edit_pro.set_tooltip_text('Edit profile')
        edit_pro.connect('activate', self.window_profiles_modify)
        edit_pro.show()
        separator = gtk.SeparatorMenuItem()
        separator.show()
        sel_key, sel_mod = gtk.accelerator_parse('<Control>A')
        select = gtk.ImageMenuItem('gtk-select-all')
        select.add_accelerator('activate', accel_group, sel_key,
                               sel_mod, gtk.ACCEL_VISIBLE)
        select.set_tooltip_text('Select all server listed')
        select.connect('activate', self.select_all_list)
        select.show()
        unsel_key, unsel_mod = gtk.accelerator_parse('<Control>U')
        unselect = gtk.ImageMenuItem('gtk-unselect')
        unselect.add_accelerator('activate', accel_group, unsel_key,
                                 unsel_mod, gtk.ACCEL_VISIBLE)
        unselect.set_tooltip_text('Unselect all server listed')
        unselect.connect('activate', self.uselect_all_list)
        unselect.show()

        menu = gtk.Menu()
        menu.append(edit_pro)
        menu.append(self._gen_edit_submenu_server(accel_group))
        menu.append(separator)
        menu.append(select)
        menu.append(unselect)
        item_edit = gtk.MenuItem('Edit')
        item_edit.set_submenu(menu)
        item_edit.set_right_justified(True)
        item_edit.show()
        return item_edit

    def _gen_edit_submenu_server(self, accel_group):
        all_key, all_mod = gtk.accelerator_parse('F4')
        mod_all = gtk.ImageMenuItem('gtk-server-mod-all')
        mod_all.add_accelerator('activate', accel_group, all_key,
                                all_mod, gtk.ACCEL_VISIBLE)
        mod_all.set_tooltip_text('Modify all server')
        mod_all.connect('activate', self.window_server_modify, 'all')
        mod_all.show()

        sel_key, sel_mod = gtk.accelerator_parse('F5')
        mod_sel = gtk.ImageMenuItem('gtk-server-mod')
        mod_sel.add_accelerator('activate', accel_group, sel_key,
                                sel_mod, gtk.ACCEL_VISIBLE)
        mod_sel.set_tooltip_text('Modify selected server')
        mod_sel.connect('activate', self.window_server_modify,
                         'selected', self.servers_active)
        mod_sel.show()

        menu = gtk.Menu()
        menu.append(mod_all)
        menu.append(mod_sel)
        item_mod = gtk.ImageMenuItem('gtk-server')
        item_mod.set_submenu(menu)
        item_mod.set_right_justified(True)
        item_mod.show()
        return item_mod

    def _gen_menu_option(self, accel_group):
        pref_key, pref_mod = gtk.accelerator_parse('<Control>P')
        item_preference = gtk.ImageMenuItem('gtk-preferences')
        item_preference.add_accelerator('activate', accel_group, pref_key,
                                        pref_mod, gtk.ACCEL_VISIBLE)
        item_preference.connect('activate', self.window_preferences)
        item_preference.show()
        plug_key, plug_mod = gtk.accelerator_parse('<Shift>P')
        item_plugins = gtk.ImageMenuItem('gtk-plugins')
        item_plugins.add_accelerator('activate', accel_group, plug_key,
                                     plug_mod, gtk.ACCEL_VISIBLE)
        item_plugins.connect('activate', self.window_plugins)
        item_plugins.show()

        menu = gtk.Menu()
        menu.append(item_preference)
        menu.append(item_plugins)
        option_item = gtk.MenuItem('Options')
        option_item.set_submenu(menu)
        option_item.set_right_justified(True)
        option_item.show()
        return option_item

    def _gen_menu_help(self, accel_group):
        item_website=gtk.ImageMenuItem('gtk-website')
        item_website.connect('activate', self.open_website)
        item_website.show()
        separator = gtk.SeparatorMenuItem()
        separator.show()
        item_about=gtk.ImageMenuItem('gtk-about')
        item_about.connect('activate', self.window_about)
        item_about.show()
        
        menu = gtk.Menu()
        menu.append(item_website)
        menu.append(separator)
        menu.append(item_about)
        help_item=gtk.MenuItem('Help')
        help_item.set_submenu(menu)
        help_item.set_right_justified(True)
        help_item.show()
        return help_item

    def create_toolbar(self):
        vbox = Gtk().make_vbox()
        handlebox = gtk.HandleBox()
        toolbar = Gtk().make_toolbar()
        
        icon_new = Gtk().make_image({'stock':gtk.STOCK_NEW,
                                     'size':gtk.ICON_SIZE_BUTTON})
        toolbar.append_item('New', 'New Server', 'Private',
                            icon_new, self.window_server_add)
        toolbar.append_space()

        icon_exp = Gtk().make_image({'stock':gtk.STOCK_SAVE_AS,
                                     'size':gtk.ICON_SIZE_BUTTON})
        toolbar.append_item('Export', 'Export Servers', 'Private',
                            icon_exp, self.window_server_export)
        icon_imp = Gtk().make_image({'stock':gtk.STOCK_SAVE,
                                     'size':gtk.ICON_SIZE_BUTTON})
        toolbar.append_item('Import', 'Import Servers', 'Private',
                            icon_imp, self.window_server_import)
        toolbar.append_space()
        
        icon_pref = Gtk().make_image({'stock':gtk.STOCK_PREFERENCES,
                                      'size':gtk.ICON_SIZE_BUTTON})
        toolbar.append_item('Preferences', 'Preferences', 'Private',
                            icon_pref, self.window_preferences)
        toolbar.append_space()
        
        icon_quit = Gtk().make_image({'stock':gtk.STOCK_QUIT,
                                      'size':gtk.ICON_SIZE_BUTTON})
        toolbar.append_item('Quit', 'Quit', 'Private',
                            icon_quit, gtk.main_quit)
        
        handlebox.add(toolbar)
        handlebox.show()
        vbox.pack_start(handlebox, True, True, 0)
        vbox.show()
        return vbox

    def create_frame_summary(self):
        vbox = Gtk().make_vbox({'spacing':2})
        
        frame_search = Gtk().make_frame({'name':'Search'})
        hbox_search = Gtk().make_hbox({'spacing':2, 'border':8})

        label_names = ['Address', 'Hostname', 'System', 'Comment']
        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)

        entry_names = ['addr', 'host', 'system', 'comment']
        entrys = dict((i,Gtk().make_entry()) for i in entry_names)
        [entrys[i].connect('activate', self.load_machines) for i in entrys]

        button_find = Gtk().make_button(self.load_machines, gtk.STOCK_FIND)
        button_clear = Gtk().make_button(self.clear_fields_find, gtk.STOCK_CLEAR)

        for i in label_names:
            index = label_names.index(i)
            hbox_search.pack_start(label_dict[label_names[index]],False,False,4)
            hbox_search.pack_start(entrys[entry_names[index]],True,True,4)
        hbox_search.pack_start(button_find, False, False, 5)
        hbox_search.pack_start(button_clear, False, False, 5)
        frame_search.add(hbox_search)

        frame_machine = Gtk().make_frame({'name':'Machines'})
        hbox_machines = Gtk().make_hbox({'spacing':3, 'border':8})
        
        machines_list = self.create_list_machines()
        hbox_machines.pack_start(machines_list, True, True, 5)
        frame_machine.add(hbox_machines)
        
        vbox.pack_start(frame_search, False, True, 0)
        vbox.pack_start(frame_machine, True, True, 0)

        self.entrys = entrys
        return vbox

    def create_list_machines(self):
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_border_width(10)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_vbox = Gtk().make_vbox()
        scroll_vbox.pack_start(scrolledwindow, True)
        
        model = gtk.TreeStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_STRING, gobject.TYPE_STRING,
                              gobject.TYPE_BOOLEAN)
        model.set_sort_column_id(3, gtk.SORT_ASCENDING)
        treeview = gtk.TreeView(model)
        treeview.columns_autosize()
        treeview.connect('button_press_event', self.list_right_button)
        treeview.set_reorderable(True)
        cell = gtk.CellRendererText()
        cell.set_property('foreground-set', True)
        cell_toggle = gtk.CellRendererToggle()
        cell_toggle.set_property('activatable', True)
        cell_toggle.connect('toggled', self.cell_toggled_cb, model)
        column_select = gtk.TreeViewColumn('Select', cell_toggle)
        column_select.add_attribute(cell_toggle, 'active', 0)
        column_ip = gtk.TreeViewColumn('Address')
        column_ip.pack_start(cell, True)
        column_ip.set_attributes(cell, text=2,
                                 foreground=7, foreground_set=8)
        column_ip.set_sort_column_id(2)
        column_ip.set_visible(True)
        column_ip.set_sort_indicator(True)
        column_host = gtk.TreeViewColumn('Hostname', cell, text=3)
        column_host.set_sort_column_id(3)
        column_user = gtk.TreeViewColumn('Username', cell, text=4)
        column_user.set_sort_column_id(4)
        column_system = gtk.TreeViewColumn('System', cell, text=5)
        column_system.set_sort_column_id(5)
        column_comments = gtk.TreeViewColumn('Comments', cell, text=6)
        column_comments.set_sort_column_id(6)
        treeview.append_column(column_select)
        treeview.append_column(column_ip)
        treeview.append_column(column_host)
        treeview.append_column(column_user)
        treeview.append_column(column_system)
        treeview.append_column(column_comments)
        treeview.show()
        scrolledwindow.add(treeview)
        scrolledwindow.show()

        self.treeview = treeview
        return scroll_vbox

    def cell_toggled_cb(self, cell, path, model):
        model[path][0] = not model[path][0]
        if model[path][0]:
            self.servers_active.append(model[path][1])
        else:
            if self.servers_active.count(model[path][1]):
                self.servers_active.remove(model[path][1])

    def list_right_button(self, treeview, event):
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
                server_id = tree_model.get_value(tree_iter, 1)
                addr = tree_model.get_value(tree_iter, 2)
                host = tree_model.get_value(tree_iter, 3)

            if event.button == 3:
                menu = self.list_menu_popup(server_id, addr, host)
                menu.popup(None, None, None, event.button, event.time)
            elif event.button == 1:
                if event.type == gtk.gdk._2BUTTON_PRESS:
                    self.window_server_modify(None, 'single', [str(server_id)])

    def list_menu_popup(self, server_id, srv_ip, srv_host):
        menu = gtk.Menu()
        # Generator file_menu
        plugins_menu = gtk.Menu()
        # plugins_menu.append(send_file)
        # plugins_menu.append(get_file)
        plugins = gtk.ImageMenuItem('gtk-plugins')
        plugins.set_submenu(plugins_menu)
        plugins.show()
        # Generator separator
        separator_opt = gtk.SeparatorMenuItem()
        separator_opt.show()
        edit = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        edit.connect('activate', self.window_server_modify,
                     'single', [str(server_id)])
        edit.show()
        remove = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        remove.connect('activate', self.confirm_server_remove, server_id)
        remove.show()
        menu.append(plugins)
        menu.append(separator_opt)
        menu.append(edit)
        menu.append(remove)
        return menu

    def confirm_server_remove(self, widget=None, server_id=None):
        confirmation = Gtk().delete_question(server_id)
        if confirmation:
            Servers().delete(server_id)
            self.load_machines()

    def select_all_list(self, widget=None):
        model = self.treeview.get_model()
        tree_iter = model.get_iter_first()
        while tree_iter:
            status = model.get_value(tree_iter, 0)
            server_id = model.get_value(tree_iter, 1)
            if not (server_id in self.servers_active):
                self.servers_active.append(server_id)
            model.set_value(tree_iter, 0, True)
            tree_iter = model.iter_next(tree_iter)

    def uselect_all_list(self, widget=None):
        model = self.treeview.get_model()
        tree_iter = model.get_iter_first()
        while tree_iter:
            status = model.get_value(tree_iter, 0)
            server_id = model.get_value(tree_iter, 1)
            if (server_id in self.servers_active):
                self.servers_active.remove(server_id)
            model.set_value(tree_iter, 0, False)
            tree_iter = model.iter_next(tree_iter)
            
    def load_machines(self, widget=None, event=None):
        self.show_machines(self.search_machines())
        # Agent(self.search_machines, [], [self.show_machines]).start()

    def search_machines(self, widget=None):
        server_list = {}
        values = dict((i,self.entrys[i].get_text()) for i in self.entrys)
        for i in [entry for entry in values if values[entry]]:
                output = Querys().like_servers(self._profile, i, values[i], True)
                servers = [x for x in output if not server_list.has_key(x['id'])]
                for i in servers:
                    server_list[i['id']] = i
        return server_list

    def show_machines(self, server_dict={}):
        self.treeview.set_sensitive(False)
        model = self.treeview.get_model()
        model.clear()

        if not server_dict:
            server_dict = Querys().get_profile_servers(self._profile)
        
        for i in server_dict:
            selected = self.servers_active.count(str(server_dict[i]['id']))
            model.append(None, (selected, server_dict[i]['id'],
                                server_dict[i]['addr'],
                                server_dict[i]['host'],
                                server_dict[i]['user'],
                                server_dict[i]['system'],
                                server_dict[i]['comment'], '#007700', False))
        self.treeview.set_sensitive(True)

    def clear_fields_find(self, widget=None):
        [self.entrys[i].set_text('') for i in self.entrys]
        self.load_machines()

    def create_statusbar(self):
        statusbar = Gtk().make_statusbar()
        context_id = statusbar.get_context_id('pyaejokuaa')
        statusbar.push(context_id, '[Info] Started!')

        self.statusbar = statusbar
        return statusbar

    def update_statusbar(self, msg):
        context_id = self.statusbar.get_context_id('pyaejokuaa')
        self.statusbar.push(context_id, msg)
                            
    def open_website(self, widget=None):
        Gtk().open_url(url='http://www.sergiotocalini.com.ar')

    def window_about(self, widget=None):
        AboutWindow(self.window)

    def window_login(self, widget=None):
        cmds = [self._set_profile]
        LoginWindow(callbacks = cmds)

    def window_plugins(self, widget=None):
        PluginsWindow(self.window, self._profile)

    def window_preferences(self, widget=None):
        cmds = [self.update_statusbar, self._load_preferences]
        PreferencesWindow(self.window, cmds)

    def window_profiles_add(self, widget=None):
        cmds = [self.update_statusbar]
        ProfilesAddWindow(self.window, cmds)

    def window_profiles_modify(self, widget=None):
        cmds = [self._set_profile]
        ProfilesSwitch_Window(self.window, self._profile, cmds)

    def window_profiles_switch(self, widget=None):
        cmds = [self._set_profile]
        ProfilesSwitch_Window(self.window, self._profile, cmds)

    def window_server_add(self, widget=None):
        cmds = [self.load_machines, self.update_statusbar]
        ServerAddWindow(self._profile, self._password, self.window, cmds)

    def window_server_export(self, widget=None):
        cmds = [self.load_machines, self.update_statusbar]
        ServerExportWindow(self._profile, self._password, self.window, cmds)

    def window_server_import(self, widget=None):
        cmds = [self.load_machines, self.update_statusbar]
        ServerImportWindow(self._profile, self._password, self.window, cmds)

    def window_server_modify(self, widget=None, mode=None, servers=None):
        cmds = [self.load_machines, self.update_statusbar]
        ServerModifyWindow(self._profile, self._password,
                           self.window, mode, servers, cmds)

    def close_application(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        gtk.main_quit()

def main():
    MainWindow()
    gtk.main()
    return 0

if __name__ == '__main__':
    main()
