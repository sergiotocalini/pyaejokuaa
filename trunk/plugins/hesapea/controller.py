#!/usr/bin/env python

import gtk
import vte
import os
import time
import pango

class Admin_Notebook():
    def create_notebook(self):
        notebook = gtk.Notebook()
        notebook.set_current_page(0)
        notebook.set_tab_pos(gtk.POS_LEFT)
        notebook.show()
        return notebook

    def create_frame(self, name, border=10):
        frame = gtk.Frame("")
        frame.set_border_width(border)
        frame.show()
        label = gtk.Label(name)
        label.set_alignment(0, 0.5)
        label.set_justify(True)
        label.show()
        return frame, label

    def append_tab(self, notebook, frame, label):
        page = notebook.append_page(frame,label)
        notebook.set_current_page(page)
        return page

class Admin_Terminal():
    def create_terminal(self, cmd_exit, args_show=None):
        terminal = vte.Terminal()
        terminal.connect("child-exited", cmd_exit)
        terminal.connect("show", self.show_callback, args_show)
        terminal.fork_command("bash")
        terminal.show()
        return terminal

    def show_callback(self, terminal, args=None):
        time.sleep(1)
        if args:
            terminal.feed_child(str(args))

    def load_pref_file(self, session=None):
        if session:
            from configobj import ConfigObj
            if session == "root":
                pref_file = "/root/.pyAeJokuaa/plugins/hesapea/pref.conf"
            else:
                pref_file = "/home/"+session+"/.pyAeJokuaa/plugins/hesapea/pref.conf"
            if os.path.isfile(pref_file):
                config = ConfigObj(pref_file)
                preference = {}
                for i in config:
                    preference[i] = config[i]
                return preference
            else:
                os.system("mkdir -p "+pref_file.replace("pref.conf", ""))
                config = ConfigObj()
                config.filename = pref_file
                config["font"] = "Courier 10 Pitch 9"
                config["transparent"] = False
                config.write()
            return True
        else:
           return False

    def load_preference(self, terminal, session):
        dict_pref = self.load_pref_file(session)
        for i in dict_pref:
            if i == "font":
                terminal.set_font_full(pango.FontDescription(dict_pref[i]),
                                       vte.ANTI_ALIAS_FORCE_DISABLE)
            if i == "transparent":
                if dict_pref[i] == "False":
                    terminal.set_background_transparent(False)
                else:
                    terminal.set_background_transparent(True)
        
