#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
from lib.Constructor import Gtk
from lib.Controller import Encryption, Servers
from lib.Path import APP_NAME

class ServerAddWindow():
    def __init__(self, profile, password, parent, callbacks=None):
        self._profile = profile
        self._password = password
        
        self.parent = parent
        self.parent.set_sensitive(False)

        self.callbacks = callbacks
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.set_screen(self.parent.get_screen())
        self.window.set_title('%s - New Server' %(APP_NAME))
        self.window.set_transient_for(self.parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        self.window.add(self.create_frame_add())
        self.window.show()

    def create_frame_add(self):
        vbox = Gtk().make_vbox()
        
        frame = Gtk().make_frame({'border':7})
        hbox_frame = Gtk().make_hbox({'spacing':3, 'border':5})

        vbox_label = Gtk().make_vbox()
        vbox_entry = Gtk().make_vbox()
        
        label_names = ['Address (*)', 'Hostname', 'Username (*)',
                       'Password #1 (*)', 'Password #2', 'Password #3',
                       'Port', 'System', 'Commands', 'Comments']
        entry_names = ['addr', 'host', 'user', 'passwd1', 'passwd2',
                       'passwd3', 'port', 'system', 'cmds', 'comment']

        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_label.pack_start(label_dict[i],False,False,7) for i in label_names]

        entrys = dict((i,Gtk().make_entry()) for i in entry_names)
        [vbox_entry.pack_start(entrys[i],False,False,2) for i in entry_names]
        
        entrys['passwd1'].set_visibility(False)
        entrys['passwd1'].connect('focus-in-event', self.show_entry)
        entrys['passwd1'].connect('focus-out-event', self.show_entry)
        entrys['passwd2'].set_visibility(False)
        entrys['passwd2'].connect('focus-in-event', self.show_entry)
        entrys['passwd2'].connect('focus-out-event', self.show_entry)
        entrys['passwd3'].set_visibility(False)
        entrys['passwd3'].connect('focus-in-event', self.show_entry)
        entrys['passwd3'].connect('focus-out-event', self.show_entry)
        entrys['cmds'].set_tooltip_text('Needed: Commands split by ,')

        hbox_frame.pack_start(vbox_label, True, False, 7)
        hbox_frame.pack_start(vbox_entry, False, False, 5)
        
        frame.add(hbox_frame)

        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.add_button},
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

    def add_button(self, widget=None):
        requires = ['addr', 'user', 'passwd1']
        values = self._get_form_values(requires)
        if values:
            server_dict = Encryption().AES_crypt_string(self._profile,
                                                        self._password,
                                                        values)
            if Servers().make(self._profile, server_dict) != False:
                server_dict.setdefault('host', '')
                server_dict.setdefault('addr', '')
                msg = 'Added: %(host)s (%(addr)s).' %(server_dict)
                [i('[Server] %s' %(msg)) for i in self.callbacks]
                self.close_window()
            else:
                msg = 'Error al insertar servidor.'
                title = '%s - Information' %(APP_NAME)
                Gtk().make_message({'msg':msg, 'title':title})

    def _get_form_values(self, requires):
        tmp = dict((i,self.entrys[i].get_text().decode()) for i in self.entrys)
        server = dict((i,tmp[i]) for i in tmp if tmp[i] != '')
        server.setdefault('port', u'22')
        server.setdefault('cmds', u'uname -a')
        if (all(map(lambda x: server[x] == '', server))):
            msg = 'El formulario esta vacio'
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})
            return False
        elif not (all(map(lambda x: server[x] != '', requires))):
            msg = 'Debe rellenar los campos obligatorios (*)'
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})
            return False
        else:
            return server

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
