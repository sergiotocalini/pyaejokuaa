#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
from lib.Constructor import Gtk
from lib.Controller import Servers, Encryption
from lib.DBAdmin import Querys
from lib.Path import APP_NAME

class ServerModifyWindow():
    def __init__(self, prof, passwd, parent, mode, servers=None, callbacks=None):
        self._profile = prof
        self._password = passwd

        self.parent = parent
        self.parent.set_sensitive(False)

        self.callbacks = callbacks

        self.server_list = servers
        if mode == 'all':
            server_dict = Querys().get_profile_servers(self._profile)
            
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.set_screen(parent.get_screen())
        self.window.set_title('%s - Modify' %(APP_NAME))
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        if (mode == 'selected' and not self.server_list):
            msg = 'Debe seleccionar los servidores que desea modificar'
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})
            self.close_window()
        else:
            self.window.add(self.create_frame(mode))
            self.window.show()
            if mode == 'single':
                self._load_single(self.server_list)

    def _load_single(self, server_list):
        server = Querys().get_server_info(server_list[0])
        dic_filter = dict((i,server[i]) for i in server if server[i] != None)
        [dic_filter.setdefault(o, '') for o in self.entrys.keys()]

        to_fill = Encryption().AES_crypt_string(self._profile, self._password,
                                                dic_filter, 'decrypt')
        
        [self.entrys[i].set_text(str(to_fill[i])) for i in self.entrys]
        
    def create_frame(self, mode):
        vbox = Gtk().make_vbox()
        
        frame = Gtk().make_frame({'border':7})
        hbox_frame = Gtk().make_hbox({'spacing':3})

        vbox_lab = Gtk().make_vbox({'spacing':2})
        label_names = ['Address', 'Hostname', 'Username', 'Password #1',
                       'Password #2', 'Password #3', 'Port', 'System',
                       'Comment', 'Commands']
        labels = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_lab.pack_start(labels[i], False, False, 7) for i in label_names]
        hbox_frame.pack_start(vbox_lab, True, True, 5)

        vbox_ent = Gtk().make_vbox({'spacing':2})
        entry_names = ['addr', 'host', 'user', 'passwd1', 'passwd2', 'passwd3',
                       'port', 'system', 'comment', 'cmds']
        entrys = dict((i,Gtk().make_entry()) for i in entry_names)

        [vbox_ent.pack_start(entrys[i], False, False, 2) for i in entry_names]
        hbox_frame.pack_start(vbox_ent, True, True, 5)
        frame.add(hbox_frame)

        entrys['passwd1'].set_visibility(False)
        entrys['passwd1'].connect('focus-in-event', self.show_entry)
        entrys['passwd1'].connect('focus-out-event', self.show_entry)
        entrys['passwd2'].set_visibility(False)
        entrys['passwd2'].connect('focus-in-event', self.show_entry)
        entrys['passwd2'].connect('focus-out-event', self.show_entry)
        entrys['passwd3'].set_visibility(False)
        entrys['passwd3'].connect('focus-in-event', self.show_entry)
        entrys['passwd3'].connect('focus-out-event', self.show_entry)
        if mode != 'single':
            entrys['addr'].set_sensitive(False)
            entrys['host'].set_sensitive(False)
            entrys['system'].set_sensitive(False)
        entrys['cmds'].set_tooltip_text('Needed: Commands split by ,')
            
        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.save_server,'args':mode},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(buttons, True, True, 0)

        self.entrys = entrys
        return vbox

    def show_entry(self, widget=None, data=None):
        if not widget.get_visibility():
            widget.set_visibility(True)
        else:
            widget.set_visibility(False)

    def save_server(self, mode=None):
        entrys = dict((i,self.entrys[i].get_text().decode()) for i in self.entrys)
        server = Encryption().AES_crypt_string(self._profile, self._password,
                                               dict((i,entrys[i]) for i in entrys))

        if mode != 'single':
            server = dict((i,server[i]) for i in server if server[i] != '')
            msg = 'Modify: %s servers.' %(len(self.server_list))
        else:
            msg = 'Modify: %(host)s (%(addr)s).' %(server)

        [Servers().modify(i, server) for i in self.server_list]
        [i('[Server] %s' %(msg)) for i in self.callbacks]
        self.close_window()

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
