#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
from database.DBAdmin import Querys
from lib.Constructor import Gtk
from lib.Controller import Admin_Servers

class Transfers_Window():
    def __init__(self, user, parent, srv_id, which=True, server=0):
        self.user = user
        self.query = Querys()
        self.admin_server = Admin_Servers()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_size_request(270, 200)
        self.window.set_resizable(False)
        self.window.connect("delete-event", self.close_window)
        self.parent = parent
        self.parent.set_sensitive(False)
        self.window.set_screen(parent.get_screen())
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.realize()
        self.window.set_modal(True)
        if gtk.gtk_version >= (2, 14):
            self.parent.set_parent_window(self.window.get_window())
            
        vbox = Gtk().make_vbox()
        frame = self.create_frame(which)
        bbox = Gtk().make_button_bar(2, gtk.BUTTONBOX_CENTER)
        button_ok = gtk.Button(stock=gtk.STOCK_OK)
        button_ok.show()
        button_cancel = Gtk().make_button(self.close_window, gtk.STOCK_CANCEL)
        bbox.add(button_ok)
        bbox.add(button_cancel)
        if which:
            if server == 0:
                self.window.set_title("Send File")
                button_ok.connect("clicked", self.srv_send, srv_id)
            elif server == 1:
                self.window.set_title("Send File To Selected")
                button_ok.connect("clicked", self.send_sel_srv, srv_id)
            elif server == -1:
                self.window.set_title("Send File To All")
                button_ok.connect("clicked", self.send_all_srv)
        else:
            if server == 0:
                self.window.set_title("Get File")
                button_ok.connect("clicked", self.srv_get, srv_id)
            elif server == 1:
                self.window.set_title("Get File From Selected")
                button_ok.connect("clicked", self.get_sel_srv, srv_id)
            elif server == -1:
                self.window.set_title("Get File From All")
                button_ok.connect("clicked", self.get_all_srv)

        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(bbox, True, True, 0)

        self.window.add(vbox)
        self.window.show()

    def create_frame(self, which):
        frame = Gtk().create_frames("Transfers", border=5)
        hbox = Gtk().make_hbox(spacing=3)

        vbox_labels = Gtk().make_vbox(spacing=2)

        image = Gtk().make_image(gtk.STOCK_NETWORK, -1)

        label_from = Gtk().make_label("From (*):")
        label_to = Gtk().make_label("To:")

        vbox_entrys = Gtk().make_vbox(spacing=2)
        image_file_to = Gtk().make_image(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        image_file_from = Gtk().make_image(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.entry_from = Gtk().make_entry()
        self.entry_to = Gtk().make_entry(tooltip="If not complete this field, the file gets on ~/.")

        hbox_file_to = Gtk().make_hbox()
        button_file_to = gtk.Button()
        button_file_to.set_tooltip_text("Select file.")
        button_file_to.connect("pressed", self.open_file_dialog,
                               self.entry_to)
        button_file_to.show()
        button_file_to.add(image_file_to)
        hbox_file_to.pack_start(self.entry_to, False, False)
        hbox_file_to.pack_start(button_file_to, False, False)

        hbox_file_from = Gtk().make_hbox()
        button_file_from = gtk.Button()
        button_file_from.set_tooltip_text("Select file.")
        button_file_from.connect("pressed", self.open_file_dialog,
                                 self.entry_from)
        button_file_from.show()
        button_file_from.add(image_file_from)
        hbox_file_from.pack_start(self.entry_from, False, False)
        hbox_file_from.pack_start(button_file_from, False, False)

        if which:
            self.entry_from.set_editable(False)
            button_file_to.set_sensitive(False)
        else:
            self.entry_to.set_editable(False)
            button_file_from.set_sensitive(False)

        vbox_labels.pack_start(label_from, False, False, 7)
        vbox_labels.pack_start(label_to, False, False, 7)
        vbox_entrys.pack_start(hbox_file_from, False, False, 2)
        vbox_entrys.pack_start(hbox_file_to, False, False, 2)

        hbox.pack_start(vbox_labels, True, False, 2)
        hbox.pack_start(vbox_entrys, True, False, 2)

        vbox = Gtk().make_vbox()

        vbox.pack_start(image, True, True, 0)
        vbox.pack_start(hbox, True, True, 0)
        
        frame.add(vbox)
        return frame

    def open_file_dialog(self, widget=None, selected_file=None):
        dict_filters = {"TXT":["*.txt"], "Script":["*.sh", "*.ksh"]}
        Gtk().open_file_dialog(selected_file, "Open", dict_filters)

    def srv_get(self, widget, srv_id):
        srv = {srv_id:self.admin_server.load_information_server(srv_id)}
        remotepath = self.entry_from.get_text()
        localpath = self.entry_to.get_text()
        if remotepath == "": remotepath = None
        if localpath == "": localpath = None
        if remotepath:
            if (localpath):
                if (not localpath.endswith("/")):
                    res=self.admin_server.SSH_get_files_on_servers(srv,
                                                                   remotepath,
                                                                   None,
                                                                   localpath)
                    self.close_window()
                    self.open_show_transfer(res, "get")
                    return res
                else:
                    Gtk().message("You need specific where save the file.")
            else:
                res=self.admin_server.SSH_get_files_on_servers(srv,
                                                               remotepath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
        else:
            Gtk().message("Fill in the required fields.")

    def get_sel_srv(self, widget, srv_id):
        srv = {}
        if not srv_id:
            Gtk().message("You need select servers.")
            self.close_window()
            return False
        srv_id.sort()
        for i in srv_id:
            srv[i] = self.admin_server.load_information_server(i)
        remotepath = self.entry_from.get_text()
        localpath = self.entry_to.get_text()
        if remotepath == "": remotepath = None
        if localpath == "": localpath = None
        if remotepath:
            if (localpath):
                if (not localpath.endswith("/")):
                    res=self.admin_server.SSH_get_files_on_servers(srv,
                                                                   remotepath,
                                                                   None,
                                                                   localpath)
                    self.close_window()
                    self.open_show_transfer(res, "get")
                    return res
            else:
                res=self.admin_server.SSH_get_files_on_servers(srv,
                                                               remotepath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
        else:
            Gtk().message("Fill in the required fields.")

    def get_all_srv(self, widget):
        remotepath = self.entry_from.get_text()
        localpath = self.entry_to.get_text()
        if remotepath == "": remotepath = None
        if localpath == "": localpath = None
        if remotepath:
            if (localpath) and (not localpath.endswith("/")):
                res=self.admin_server.SSH_get_files_on_servers(None,
                                                               remotepath,
                                                               self.user,
                                                               localpath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
            else:
                res=self.admin_server.SSH_get_files_on_servers(None,
                                                               remotepath,
                                                               self.user)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
        else:
            Gtk().message("Fill in the required fields.")

    def srv_send(self, widget, srv_id):
        srv = {srv_id:self.admin_server.load_information_server(srv_id)}
        localpath = self.entry_from.get_text()
        remotepath = self.entry_to.get_text()
        if localpath == "": localpath = None
        if remotepath == "": remotepath = None
        if localpath:
            if (remotepath) and (not remotepath.endswith("/")):
                res=self.admin_server.SSH_send_files_on_servers(srv,
                                                                localpath,
                                                                None,
                                                                remotepath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
            else:
                res=self.admin_server.SSH_send_files_on_servers(srv,
                                                                localpath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
        else:
            Gtk().message("Fill in the required fields.")

    def send_sel_srv(self, widget, srv_id):
        srv = {}
        if not srv_id:
            Gtk().message("You need select servers.")
            self.close_window()
            return False
        srv_id.sort()
        for i in srv_id:
            srv[i] = self.admin_server.load_information_server(i)
        localpath = self.entry_from.get_text()
        remotepath = self.entry_to.get_text()
        if localpath == "": localpath = None
        if remotepath == "": remotepath = None
        if localpath:
            if (remotepath) and (not remotepath.endswith("/")):
                res=self.admin_server.SSH_send_files_on_servers(srv,
                                                                localpath,
                                                                None,
                                                                remotepath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
            else:
                res=self.admin_server.SSH_send_files_on_servers(srv,
                                                                localpath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
        else:
            Gtk().message("Fill in the required fields.")

    def send_all_srv(self, widget):
        localpath = self.entry_from.get_text()
        remotepath = self.entry_to.get_text()
        if localpath == "": localpath = None
        if remotepath == "": remotepath = None
        if localpath:
            if (remotepath) and (not remotepath.endswith("/")):
                res=self.admin_server.SSH_send_files_on_servers(None,
                                                                localpath,
                                                                self.user,
                                                                remotepath)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
            else:
                res=self.admin_server.SSH_send_files_on_servers(None,
                                                                localpath,
                                                                self.user)
                self.close_window()
                self.open_show_transfer(res, "get")
                return res
        else:
            Gtk().message("Fill in the required fields.")

    def open_show_transfer(self, result, which=None):
        Show_Transfers_Result_Window(self.parent, result, which)

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)

class Show_Transfers_Result_Window():
    def __init__(self, parent, result, which=None):
        self.admin_server = Admin_Servers()
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_size_request(350, 180)
        self.window.set_resizable(False)
        self.window.connect("delete-event", self.close_window)
        self.parent = parent
        self.parent.set_sensitive(False)
        self.window.set_title("Show Result")
        self.window.set_screen(parent.get_screen())
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.realize()
        self.window.set_modal(True)
        if gtk.gtk_version >= (2, 14):
            self.parent.set_parent_window(self.window.get_window())

        vbox = self.create_summary_show(result, which)
        
        self.window.add(vbox)
        self.window.show()

    def create_summary_show(self, result, which):
        vbox = Gtk().make_vbox()
        hbox = Gtk().make_hbox(border=20, spacing=3)
        image_information = Gtk().make_image(gtk.STOCK_DIALOG_INFO, -1)
        
        vbox_results = Gtk().make_vbox()
        
        count_ok, count_fail = self.count_result(result)
        title_resume = "Tranferencias"
        ok_result = str(count_ok)+" exitosas."
        cancel_result = str(count_fail)+" fallidas."
        label_title = Gtk().make_label(title_resume,font="9")
        label_ok = Gtk().make_label(ok_result,font="7")
        label_cancel = Gtk().make_label(cancel_result,font="7")

        vbox_results.pack_start(label_title, True, True, 0)
        vbox_results.pack_start(label_ok, True, True, 0)
        vbox_results.pack_start(label_cancel, True, True, 0)
        
        hbox.pack_start(image_information, True, True, 0)
        hbox.pack_start(vbox_results, True, True, 2)

        expander = Gtk().make_expander("Debug", self.expanded_result, result)
        
        bbox = Gtk().make_one_button_bar(self.close_window)
        vbox.pack_start(hbox, False, False, 2)
        vbox.pack_start(expander, True, True, 2)
        vbox.pack_start(bbox, False, False, 2)
        
        return vbox

    def expanded_result(self, widget, data, result):
        if widget.get_expanded():
            box = self.make_box_result(result)
            widget.add(box)
            self.window.set_size_request(400, 300)
        else:
            widget.remove(widget.child)
            self.window.set_size_request(350, 180)

    def make_box_result(self, result):
        hbox = Gtk().make_hbox(border=5)
        view = gtk.TextView()
        view.set_editable(False)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        scrolled_window.add(view)
        buffer_text = view.get_buffer()
        archive = self.transform_result(result)
        result_text = ""
        for i in archive:
            result_text = result_text + i
        iter_number = buffer_text.get_iter_at_offset(0)
        buffer_text.insert(iter_number, result_text)
        scrolled_window.show_all()
        hbox.pack_start(scrolled_window, True, True, 2)
        return hbox

    def transform_result(self, result):
        convertion = []
        for i in result:
            srv_id = result[i]["id"]
            srv = self.admin_server.load_information_server(srv_id)
            if not srv["host"]:
                host = ""
            else:
                host = " ( " + srv["host"] + " )"
            text = "=== " + srv["ip"] + host + " ===\n"
            if result[i]["auth"]:
                text = text + "\tAuthentification... OK!\n"
                if result[i].has_key("get"):
                    if (result[i]["get"]<>"No such file") and (result[i]["get"]<>"Permission denied"):
                        text = text + "\tGet Transfer... OK!\n\n"
                    else:
                        text = text + "\tGet Transfer... FAIL! ( " + result[i]["get"] + " )\n\n"
                else:
                    if (result[i]["send"]<>"No such file") and (result[i]["send"]<>"Permission denied"):
                        text = text + "\tSend Transfer... OK!\n\n"
                    else:
                        text = text + "\tSend Transfer... FAIL! ( " + result[i]["send"] + " )\n\n"
            else:
                text = text + "\tAuthentification... FAIL!\n"
                if result[i].has_key("get"):
                    text = text + "\tGet Transfer... FAIL!\n\n"
                else:
                    text = text + "\tSend Transfer... FAIL!\n\n"
            convertion.append(text)
        return convertion

    def count_result(self, result):
        count_ok = 0
        count_fail = 0
        for i in result:
            if result[i]["auth"]:
                if result[i].has_key("get"):
                    if (result[i]["get"]<>"No such file") and (result[i]["get"]<>"Permission denied"):
                        count_ok = count_ok + 1
                    else:
                        count_fail = count_fail + 1
                elif result[i].has_key("send"):
                    if (result[i]["send"]<>"No such file") and (result[i]["send"]<>"Permission denied"):
                        count_ok = count_ok + 1
                    else:
                        count_fail = count_fail + 1
            else:
                count_fail = count_fail + 1
        return count_ok, count_fail

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
