#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
import os
from DateTime import DateTime
from lib.Constructor import Gtk
from lib.Controller import Admin_Servers

class Execute_Window():
    def __init__(self, parent, notebook, which, srv=None, user=None):
        self.admin_server = Admin_Servers()
        
        self.template_active = []
        
        self.session = os.environ['LOGNAME']
        
        self.parent = parent
        self.parent.set_sensitive(False)

        self.user = user       
        self.notebook = notebook

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_size_request(400, 450)
        self.window.set_resizable(False)
        self.window.connect("delete-event", self.close_window)
        self.window.set_screen(parent.get_screen())
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.realize()
        self.window.set_modal(True)

        if gtk.gtk_version >= (2, 14):
            self.parent.set_parent_window(self.window.get_window())

        self.server_info, self.subject = self.load_srv_information(which,srv)
        vbox, self.treeview = self.create_execute_frame()
        self.change_scripts(None, -1)
        self.load_templates_list(self.treeview)
        
        if which == 1:
            if not srv:
                Gtk().message("You should select any server to use this function.")
                self.close_window()
            else:
                self.window.add(vbox)
                self.window.show()
        else:
            self.window.add(vbox)
            self.window.show()

    def create_execute_frame(self):
        vbox = Gtk().make_vbox(spacing=3)
        frame = Gtk().create_frames("Execute", border=5)
        vbox_exe = Gtk().make_vbox(spacing=2, border=5)
        label_script = "Commands from profiles"
        label_manual = "Manual commands"
        label_template = "Templates"
        button_notmp = Gtk().make_radiobutton(label_script,
                                                         self.change_scripts,
                                                         -1)
        button_man = Gtk().make_radiobutton(label_manual,
                                                       self.change_scripts,
                                                       0,
                                                       button_notmp)
        button_tmp = Gtk().make_radiobutton(label_template,
                                                       self.change_scripts,
                                                       1,
                                                       button_notmp)
        hbox_man = Gtk().make_hbox(spacing=5)
        tooltip = "Example: uname -a,date,hostname,uptime"
        self.entry_man = Gtk().make_entry(tooltip=tooltip)
        hbox_man.pack_start(self.entry_man, True, True, 20)

        hbox_tmp = Gtk().make_hbox(spacing=2)
        self.frame_tmp = Gtk().create_frames("Templates",border=5)
        templates_vbox, treeview = self.create_lists_templates()
        box_add_tmp = Gtk().make_vbox()
        add_tmp = Gtk().make_event_box("Add Template",
                                                  self.load_admin_templates)
        box_add_tmp.pack_start(add_tmp, True, True, 0)
        templates_vbox.pack_start(box_add_tmp, False, False, 0)
        
        self.frame_tmp.add(templates_vbox)
        hbox_tmp.pack_start(self.frame_tmp, True, True, 15)

        expander = Gtk().make_expander("Servers list",
                                                  self.expanded_result,
                                                  None)
        
        vbox_exe.pack_start(button_notmp, False, False, 0)
        vbox_exe.pack_start(button_man, False, False, 0)
        vbox_exe.pack_start(hbox_man, False, False, 0)
        vbox_exe.pack_start(button_tmp, False, False, 0)
        vbox_exe.pack_start(hbox_tmp, True, True, 2)
        vbox_exe.pack_start(expander, False, False, 3)
        frame.add(vbox_exe)
        
        button_run = Gtk().make_button(self.run_button,
                                                  gtk.STOCK_EXECUTE)
        button_quit = Gtk().make_button(self.close_window,
                                                   gtk.STOCK_CLOSE)
        bbox = Gtk().make_button_bar()
        bbox.add(button_run)
        bbox.add(button_quit)
        
        vbox.pack_start(frame, True, True, 2)
        vbox.pack_start(bbox, False, False, 2)
        
        return vbox, treeview

    def change_scripts(self, widget, data):
        if data == -1:
            self.frame_tmp.set_sensitive(False)
            self.entry_man.set_sensitive(False)
        elif data == 0:
            self.frame_tmp.set_sensitive(False)
            self.entry_man.set_sensitive(True)
        elif data == 1:
            self.entry_man.set_sensitive(False)
            self.frame_tmp.set_sensitive(True)
        self.use_templates = data

    def create_lists_templates(self):
        templates = gtk.ScrolledWindow()
        templates.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        templates.show()
        templates_vbox = Gtk().make_vbox(border=10)
        templates_vbox.pack_start(templates, True)

        model = gtk.TreeStore(gobject.TYPE_BOOLEAN, gobject.TYPE_STRING)
        model.set_sort_column_id(1, gtk.SORT_ASCENDING)
        treeview = gtk.TreeView(model)
        treeview.connect("button_press_event", self.list_right_button)
        treeview.show()
        
        cell = gtk.CellRendererText()
        cell_toggle = gtk.CellRendererToggle()
        cell_toggle.set_property("activatable", True)
        cell_toggle.connect("toggled", self.cell_toggled_cb, model)
                
        column_active = gtk.TreeViewColumn(None, cell_toggle)
        column_active.add_attribute(cell_toggle, "active", 0)
        column_template = gtk.TreeViewColumn(None, cell, text=1)
        
        treeview.append_column(column_active)
        treeview.append_column(column_template)
        templates.add_with_viewport(treeview)
        
        return templates_vbox, treeview

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
                    template = tree_model.get_value(tree_iter, 1)
                    menu = self.list_menu_popup(template)
                    menu.popup(None, None, None, event.button, event.time)
            return 1

    def list_menu_popup(self, template):
        menu = gtk.Menu()
        item_edit = gtk.ImageMenuItem(gtk.STOCK_EDIT)
        item_edit.connect("activate", self.load_admin_templates,
                          None, template)
        item_edit.show()
        item_remove = gtk.ImageMenuItem(gtk.STOCK_DELETE)
        item_remove.connect("activate", self.delete_template, template)
        item_remove.show()
        menu.append(item_edit)
        menu.append(item_remove)
        return menu

    def cell_toggled_cb(self, cell, path, model):
        model[path][0] = not model[path][0]
        if model[path][0]:
            self.template_active.append(model[path][1])
        else:
            if self.template_active.count(model[path][1]):
                self.template_active.remove(model[path][1])

    def expanded_result(self, widget, data, result):
        if widget.get_expanded():
            box = self.make_details_box(self.server_info)
            widget.add(box)
            self.window.set_size_request(400, 500)
        else:
            widget.remove(widget.child)
            self.window.set_size_request(400, 450)

    def make_details_box(self, srv_info):
        box, self.view = Gtk().textview_box(None, False)
        buffer_text = self.view.get_buffer()
        text = ""
        servers = []
        for i in srv_info:
            servers.append(srv_info[i]["host"] + "\n")
        servers.sort()
        for i in servers:
            text = text + i 
        iter_number = buffer_text.get_iter_at_offset(0)
        buffer_text.insert(iter_number, text)
        return box

    def create_frame_results(self, subject):
        date_time = DateTime()
        date = str(date_time.Date()) + " " + str(date_time.Time())
        page, frame = self.add_tab_notebook(subject + ": "+ date)
        vbox = Gtk().make_vbox(spacing=3)
        list_vbox, treeview = self.create_list_show_results()
        box_vbox, self.buffer_text = self.create_box_show()
        button_export = Gtk().make_button(self.save_file_export,
                                                     "gtk-export",
                                                     treeview)
        button_close = Gtk().make_button(self.del_tab_notebook,
                                                    "gtk-close")
        button_bar = Gtk().make_button_bar()
        button_bar.add(button_export)
        button_bar.add(button_close)
        vbox.pack_start(list_vbox, True, True, 0)
        vbox.pack_start(box_vbox, True, True, 0)
        vbox.pack_start(button_bar, False, True, 1)
        frame.add(vbox)
        return frame, treeview, self.buffer_text

    def save_file_export(self, treeview):
        if self.session == "root":
            folder = "/root/.pyAeJokuaa/logs/"
        else:
            folder = "/home/" + self.session + "/.pyAeJokuaa/logs/"

        dict_filters = {"LOG":["*.log"]}
        date_time = DateTime()
        date = str(date_time.Date().replace("/", ""))
        time = str(date_time.Time().replace(":", ""))
        filename = "pyAeJokuaa." + date + "_" + time + ".log"
        selected_file = Gtk().save_file_dialog(folder=folder,
                                                          filters=dict_filters,
                                                          savefile=filename)
        if selected_file:
            result = self.export_result(treeview, selected_file)
            if result:
                Gtk().message("The export has been successful.")
            else:
                Gtk().message("Exportation has been mistaken.",
                                         message=gtk.MESSAGE_WARNING)

    def export_result(self, treeview, outfile=None):
        tree_model = treeview.get_model()
        tree_iter = tree_model.get_iter_first()
        try:
            if not outfile:
                archive = open("/tmp/pyaejokuaa.log", "w+b")
            else:
                archive = open(outfile, "w+b")

            date_time = DateTime()
            archive.write("Date: " + date_time.Date() + "\n")
            archive.write("Time: " + date_time.Time() + "\n\n")
            count = 0
            while tree_iter:
                archive.write("###########################\n")
                archive.write(tree_model.get_value(tree_iter, 0) + "\n")
                archive.write("###########################\n")
                archive.write(tree_model.get_value(tree_iter, 1))
                tree_iter = tree_model.iter_next(tree_iter)
                count = count + 1
            archive.write("\n\nServers count: " + str(count) + "\n")
            archive.write("Powered by pyAeJokuaa, for more information go to http://code.google.com/p/pyaejokuaa\n")
            archive.close()
            return True
        except:
            return False

    def create_list_show_results(self):
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_border_width(10)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_vbox = Gtk().make_vbox()
        scroll_vbox.pack_start(scrolledwindow, True)
        model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        model.set_sort_column_id(0, gtk.SORT_ASCENDING)
        treeview = gtk.TreeView(model)
        treeview.connect("button_press_event", self.select_button)
        treeview.show()
        cell = gtk.CellRendererText()
        column_srv = gtk.TreeViewColumn("Server", cell, text=0)
        column_srv.set_sort_column_id(0)
        column_res = gtk.TreeViewColumn("Result", cell, text=1)
        treeview.append_column(column_srv)
        treeview.show()
        scrolledwindow.add_with_viewport(treeview)
        scrolledwindow.show()
        return scroll_vbox, treeview

    def create_box_show(self):
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_border_width(10)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll_vbox = Gtk().make_vbox()
        scroll_vbox.pack_start(scrolledwindow, True)
        view = gtk.TextView()
        view.set_editable(False)
        buffer_text = view.get_buffer()
        view.show()
        scrolledwindow.add(view)
        scrolledwindow.show()
        return scroll_vbox, buffer_text

    def select_button(self, treeview, event):
        if event.button == 1:
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
                    server = tree_model.get_value(tree_iter, 0)
                    result = tree_model.get_value(tree_iter, 1)
                    self.buffer_text.set_text("")
                    iter=self.buffer_text.get_iter_at_offset(0)
                    self.buffer_text.insert(iter, result)
            return 1

    def show_results(self, result, list_cmd, subject):
        frame, treeview, buffer_text = self.create_frame_results(subject)
        model = treeview.get_model()
        model.clear()
        for i in result:
            text = ""
            if (not result[i]["host"]) or (result[i]["host"] == ""):
                server = result[i]["ip"]
            else:
                server = result[i]["ip"] + " (" + result[i]["host"] + ")"
            if result[i]["commands"]:
                if list_cmd:
                    order = list_cmd
                else:
                    order = result[i]["commands"]
                    
                for x in order:
                    if (not result[i]["host"]) or (result[i]["host"] == ""):
                        text = text + result[i]["ip"] + ":/ # " + x + "\n"
                    else:
                        text = text + result[i]["host"] + ":/ # " + x + "\n"
                    for res in result[i]["commands"][x]:
                        text = text + res

                if result[i]["auth"]:
                    model.append([server, text])
                else:
                    model.append([server, server + ": Connection error."])
            else:
                if result[i]["auth"]:
                    model.append([server, text])
                else:
                    model.append([server, server + ": Connection error."])

    def load_templates_scripts(self, list_templates):
        from configobj import ConfigObj
        configfile = ConfigObj(self.template_file)
        scripts = []
        for i in list_templates:
            for x in configfile[i]:
                if not scripts.count(x):
                    scripts.append(x)
        return scripts

    def load_templates_list(self, treeview=None):
        if not treeview:
            treeview = self.treeview
        from configobj import ConfigObj
        if self.session == "root":
            self.template_file = "/root/.pyAeJokuaa/script_templates"
        else:
            self.template_file = "/home/" + self.session + "/.pyAeJokuaa/script_templates"
        
        if not os.path.isfile(self.template_file):
            self.make_templates_list(self.template_file)

        model = treeview.get_model()
        model.clear()

        configfile = ConfigObj(self.template_file)
        for i in configfile:
            model.append(None, (False, i))

    def load_srv_information(self, which, srv_id=None):
        if which == -1:
            srv = Admin_Servers().all_servers_per_user(self.user)
            subject = "All"
        elif which == 0:
            srv = {srv_id:Admin_Servers().load_information_server(srv_id)}
            subject = "Only One"
        elif which == 1:
            srv = {}
            subject = "Selected"
            for i in srv_id:
                srv[i] = Admin_Servers().load_information_server(i)
        else:
            return False
        return srv, subject

    def make_templates_list(self, filename):
        from configobj import ConfigObj
        config = ConfigObj()
        config.filename = filename
        config["Basic Information"] = ["uname -a","hostname","date",
                                       "uptime","free","sudo -V","sudo -l"]
        config.write()

    def run_button(self, srv):
        from configobj import ConfigObj
        if self.use_templates == -1:
            result = self.execute_cmd(None, self.server_info)
            self.show_results(result, None, self.subject)            
        elif self.use_templates == 0:
            scripts = self.entry_man.get_text().split(",")
            result = self.execute_cmd(scripts, self.server_info)
            self.show_results(result, scripts, self.subject)
        elif self.use_templates == 1:
            scripts = self.load_templates_scripts(self.template_active)
            result = self.execute_cmd(scripts, self.server_info)
            self.show_results(result, scripts, self.subject)
        self.close_window()

    def execute_cmd(self, script, srv):
        if script:
            result = Admin_Servers().SSH_run_commands_on_servers(srv,None,script)
        else:
            result = Admin_Servers().SSH_run_commands_on_servers(srv)
        return result

    def delete_template(self, widget, template):
        result = Gtk().message_question("")
        if result:
            from configobj import ConfigObj
            config = ConfigObj(self.template_file)
            config.pop(template)
            config.write()
            Gtk().message("")
        self.load_templates_list()
    
    def add_tab_notebook(self, title):
        frame = Gtk().create_frames(title)
        label = Gtk().make_label(title)
        page = self.notebook.append_page(frame, label)
        return page, frame

    def del_tab_notebook(self, widget=None, notebook=None):
        if not notebook:
            notebook = self.notebook
        page = notebook.get_current_page()
        notebook.remove_page(page)
        notebook.queue_draw_area(1,1,1,1)

    def load_admin_templates(self, widget, data=None, template=None):
        if template:
            template = {"name":template,
                        "cmd":self.load_templates_scripts([template])}
        Admin_Templates(self.window, template, self.template_file)

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)

class Admin_Templates():
    def __init__(self, parent, template, filename):
        self.filename = filename
        self.parent = parent
        self.parent.set_sensitive(False)
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_size_request(350, 350)
        self.window.set_resizable(False)
        self.window.connect("delete-event", self.close_window)
        self.window.set_screen(parent.get_screen())
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.realize()
        self.window.set_modal(True)
        if gtk.gtk_version >= (2, 14):
            self.parent.set_parent_window(self.window.get_window())

        frame = self.create_frame(template)
        
        self.window.add(frame)
        self.window.show()

    def create_frame(self, template=None):
        vbox_tmp = Gtk().make_vbox()
        hbox = Gtk().make_vbox(spacing=5, border=5)
        vbox = Gtk().make_vbox(spacing=5, border=5)
        frame = Gtk().create_frames("Templates", border=3)
        hbox_title = Gtk().make_hbox(spacing=10)
        label_title = Gtk().make_label("Name")
        if template:
            self.entry_title = Gtk().make_entry(template["name"],
                                                           lenght=40)
        else:
            self.entry_title = Gtk().make_entry()
        hbox_title.pack_start(label_title, False, True, 2)
        hbox_title.pack_start(self.entry_title, True, True, 2)
        vbox_cmds = Gtk().make_vbox(spacing=5)
        text = ""
        if template:
            for i in template["cmd"]:
                text = text + i + "\n"
        frame_buffer, self.view = Gtk().textview_box("Commands",
                                                                  True)
        buffer_text = self.view.get_buffer()
        iter_number = buffer_text.get_iter_at_offset(0)
        buffer_text.insert(iter_number, text)
        vbox_cmds.pack_start(frame_buffer, True, True, 2)

        vbox.pack_start(hbox_title, False, False, 5)
        vbox.pack_start(vbox_cmds, True, True, 2)
        
        hbox.pack_start(vbox, True, True, 2)
        frame.add(hbox)

        button_run = Gtk().make_button(self.save_template,
                                       gtk.STOCK_SAVE,
                                       template)
        button_quit = Gtk().make_button(self.close_window,
                                        gtk.STOCK_CLOSE)
        bbox = Gtk().make_button_bar()
        bbox.add(button_run)
        bbox.add(button_quit)       
        
        vbox_tmp.pack_start(frame, True, True, 2)
        vbox_tmp.pack_start(bbox, False, False, 2)
        
        return vbox_tmp

    def save_template(self, template=None):
        name = self.entry_title.get_text()
        buffer_text = self.view.get_buffer()
        start = buffer_text.get_start_iter()
        end = buffer_text.get_end_iter()
        cmds = buffer_text.get_text(start, end)
        cmds = cmds.strip()
        cmds = cmds.split("\n")
        save_result = self.write_template(name, cmds, template)
        self.close_window()

    def write_template(self, template, value, template_org=None):
        from configobj import ConfigObj
        config = ConfigObj(self.filename)
        if template_org:
            config.pop(template_org["name"])
        config[template] = value
        config.write()
        return True
        
    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
