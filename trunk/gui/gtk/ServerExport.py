#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
from lib.Constructor import Gtk
from lib.Controller import Encryption, Export
from lib.DBAdmin import Querys
from lib.Path import APP_NAME

class ServerExportWindow():
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
        self.window.set_title('%s - Export' %(APP_NAME))
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)

        self.window.add(self.create_frame())
        self.window.show()

    def create_frame(self):
        vbox = Gtk().make_vbox()
        
        frame = Gtk().make_frame({'border':7})
        vbox_frame = Gtk().make_vbox()
        hbox = Gtk().make_hbox({'spacing':3, 'border':5})

        vbox_label = Gtk().make_vbox()
        vbox_entry = Gtk().make_vbox()

        label_names = ['File (*)']
        
        order = ';'.join(['addr', 'host', 'user', 'passwd1', 'passwd2',
                          'passwd3', 'port', 'system', 'comment', 'cmds'])
        
        button_list = [{'stock':gtk.STOCK_INDEX,'cmd':self.file_dialog},
                       {'stock':gtk.STOCK_PREFERENCES,'cmd':self.file_dialog,
                        'tooltip':'Setup fields order. Default order: %s' %order,
                        'sensitive':False}]
        hbox_file, entry_file = Gtk().make_entry_buttons(buttons=button_list)

        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_label.pack_start(label_dict[i],False,False,7) for i in label_names]

        entrys = {}
        entrys['filename'] = entry_file
        
        vbox_entry.pack_start(hbox_file,False,False,0)

        hbox.pack_start(vbox_label, True, False, 7)
        hbox.pack_start(vbox_entry, False, False, 5)

        expander = Gtk().make_expander({'title':'Options',
                                        'callback':self.expanded_options})
        expander.add(self.show_options())
        
        vbox_frame.pack_start(hbox, True, True, 2)
        vbox_frame.pack_start(expander, True, True, 2)
        
        frame.add(vbox_frame)

        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.export_button},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})

        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(buttons, True, True, 0)

        self.entrys = entrys
        return vbox

    def expanded_options(self, widget=None, data=None, info=None):
        if widget.get_expanded():
            widget.set_expanded(True)
        else:
            widget.set_expanded(False)

    def show_options(self, widget=None):
        hbox = Gtk().make_hbox({'spacing':5,'border':5})

        vbox_lab = Gtk().make_vbox()
        label_names = ['Format', 'Delimiter']
        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_lab.pack_start(label_dict[i], True, False, 2) for i in label_names]
        hbox.pack_start(vbox_lab, True, False, 3)

        vbox_entry = Gtk().make_vbox()
        
        cell = gtk.CellRendererText()
        combo_format = gtk.ComboBox(gtk.ListStore(gobject.TYPE_STRING,
                                                  gobject.TYPE_STRING))
        combo_format.pack_start(cell, True)
        combo_format.connect('changed', self.change_format)
        combo_format.add_attribute(cell, "text", 1)
        combo_format.show()

        vbox_entry.pack_start(combo_format, True, False, 2)

        entry_names = ['delimiter']
        entrys = dict((i,Gtk().make_entry({'name':i})) for i in entry_names)

        [vbox_entry.pack_start(entrys[i], True, False, 2) for i in entry_names]
        hbox.pack_start(vbox_entry, True, False, 3)

        entrys['delimiter'].set_text(';')
        entrys['format'] = combo_format
        self.entrys_opt = entrys

        format_opt = ['csv', 'xls']
        self.load_combo(combo_format, format_opt)

        return hbox

    def change_format(self, widget=None):
        model = widget.get_model()
        index = widget.get_active()
        if model[index][1] == "csv":
            self.entrys_opt['delimiter'].set_sensitive(True)
        else:
            self.entrys_opt['delimiter'].set_sensitive(False)

    def load_combo(self, widget, values):
        model = widget.get_model()
        counter = 0
        for i in values:
            model.append((counter, i))
            counter += 1
        widget.set_active(0)

    def file_dialog(self, widget=None, entry_file=None):
        dialog_dict = {'action':gtk.FILE_CHOOSER_ACTION_SAVE,
                       'buttons':(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                  gtk.STOCK_SAVE, gtk.RESPONSE_OK),
                       'filter':{'All':['*']},
                       'title':'%s - Export' %(APP_NAME)}
        file_selected = Gtk().make_dialog(dialog_dict)
        if file_selected != None:
            entry_file.set_text(file_selected)

    def export_button(self, widget=None):
        requires = ['filename']
        options = self._get_form_values(requires)
        if options:
            opt = ['addr', 'host', 'user', 'passwd1', 'passwd2',
                   'passwd3', 'port', 'system', 'comment', 'cmds']

            rows = []
            srvs = Querys().get_profile_servers(self._profile)
            for i in srvs:
                tmp = dict((x, srvs[i][x]) for x in srvs[i] if srvs[i][x] != None)
                server = Encryption().AES_crypt_string(self._profile,
                                                       self._password,
                                                       tmp, 'decrypt')
                [server.setdefault(x, u'') for x in opt]
                rows.append([server[x] for x in opt])

            model = self.entrys_opt['format'].get_model()
            index = self.entrys_opt['format'].get_active()
            if model[index][1] == "csv":
                options['delimiter'] = self.entrys_opt['delimiter'].get_text()
                options['extention'] = ''
                options['overwrite'] = True
                if Export().csv(rows, options) != False:
                    self.close_window()
                    msg = 'Export: %s servers were exported.'%(len(rows))
                    title = '%s - Information' %(APP_NAME)
                    [i('[Server] %s' %(msg)) for i in self.callbacks]
                    Gtk().make_message({'msg':msg, 'title':title})
            else:
                if Export().spreadsheet(rows, options) != False:
                    self.close_window()

    def _get_form_values(self, requires):
        tmp = dict((i,self.entrys[i].get_text().decode()) for i in self.entrys)
        export = dict((i,tmp[i]) for i in tmp if tmp[i] != '')
        if (all(map(lambda x: export[x] == '', export))):
            msg = 'El formulario esta vacio'
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})
            return False
        elif not (all(map(lambda x: export[x] != '', requires))):
            msg = 'Debe rellenar los campos obligatorios (*)'
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})
            return False
        else:
            return export

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
