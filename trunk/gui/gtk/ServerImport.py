#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
from lib.Constructor import Gtk
from lib.Controller import Encryption, Servers
from lib.Path import APP_NAME

class ServerImportWindow():
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
        self.window.set_screen(parent.get_screen())
        self.window.set_title('%s - Import' %(APP_NAME))
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        self.window.add(self.create_frame())
        self.window.show()

    def create_frame(self):
        vbox = Gtk().make_vbox()
        
        frame = Gtk().make_frame({'border':7})
        hbox_frame = Gtk().make_hbox({'spacing':3, 'border':5})

        vbox_label = Gtk().make_vbox()
        vbox_entry = Gtk().make_vbox()

        label_names = ['File (*)', 'Hostname', 'Username',
                       'Password #1', 'Password #2', 'Password #3',
                       'Port', 'System', 'Commands', 'Comments']
        entry_names = ['host', 'user', 'passwd1', 'passwd2',
                       'passwd3', 'port', 'system', 'cmds', 'comment']

        order = ';'.join(['addr', 'host', 'user', 'passwd1', 'passwd2',
                          'passwd3', 'port', 'system', 'comment', 'cmds'])
        
        button_list = [{'stock':gtk.STOCK_INDEX,'cmd':self.file_dialog},
                       {'stock':gtk.STOCK_PREFERENCES,'cmd':self.file_dialog,
                        'tooltip':'Setup fields order. Default order: %s' %order,
                        'sensitive':False}]
        hbox_file, entry_file = Gtk().make_entry_buttons(buttons=button_list)

        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_label.pack_start(label_dict[i],False,False,7) for i in label_names]

        entrys = dict((i,Gtk().make_entry()) for i in entry_names)
        entrys['file'] = entry_file
        
        vbox_entry.pack_start(hbox_file,False,False,0)
        [vbox_entry.pack_start(entrys[i],False,False,2) for i in entry_names]
        
        entrys['host'].set_sensitive(False)
        entrys['system'].set_sensitive(False)
        entrys['port'].set_sensitive(False)
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

        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.import_button},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})

        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(buttons, True, True, 0)

        self.entrys = entrys
        return vbox

    def file_dialog(self, widget=None, entry_file=None):
        dialog_dict = {'action':gtk.FILE_CHOOSER_ACTION_OPEN,
                       'buttons':(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_OPEN, gtk.RESPONSE_OK),
                       'filter':{'TXT':['*.txt'], 'CSV':['*.csv'],'All':['*']},
                       'title':'%s - Import' %(APP_NAME)}
        file_selected = Gtk().make_dialog(dialog_dict)
        if file_selected != None:
            entry_file.set_text(file_selected)

    def show_entry(self, widget=None, data=None):
        if not widget.get_visibility():
            widget.set_visibility(True)
        else:
            widget.set_visibility(False)

    def import_button(self, widget=None):
        requires = ['file']
        values = self._get_form_values(requires)
        if values:
            true_count = 0
            false_count = 0
            opt = ['addr', 'host', 'user', 'passwd1', 'passwd2',
                   'passwd3', 'port', 'system', 'comment', 'cmds']
            archive = open(values['file'], 'r')
            for i in archive.readlines():
                row = i.strip().split(';')
                lin = dict((x,z.decode()) for x,z in enumerate(row))
                for o in opt: lin.setdefault(opt.index(o), None)
                imp = dict((z,lin[x]) for x,z in enumerate(opt) if lin[x] != None)
                new_server = values.copy()
                new_server.update(imp)
                server = Encryption().AES_crypt_string(self._profile,
                                                       self._password,
                                                       new_server)
                server = dict((i,server[i]) for i in server if server[i] != '')
                if Servers().make(self._profile, server) != False:
                    true_count += 1
                else:
                    false_count +=1

            self.close_window()
            lines = sum([true_count, false_count])
            msg = 'Import: %s / %s was added successfully.'%(true_count,lines)
            title = '%s - Information' %(APP_NAME)
            [i('[Server] %s' %(msg)) for i in self.callbacks]
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
