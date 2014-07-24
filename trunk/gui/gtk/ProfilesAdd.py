#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
import os
import sys
from lib.Constructor import Gtk
from lib.Controller import Encryption, Profiles
from lib.DBAdmin import Querys
from lib.Path import APP_NAME

class ProfilesAddWindow():
    def __init__(self, parent, callbacks=[]):
        self.parent = parent
        self.parent.set_sensitive(False)

        self.callbacks = callbacks
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.connect('delete-event', self.close_window)
        self.window.set_title('%s - Add Profile' %(APP_NAME))
        self.window.set_screen(self.parent.get_screen())
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.realize()
        self.window.set_modal(True)

        if gtk.gtk_version >= (2, 14):
            self.parent.set_parent_window(self.window.get_window())

        self.window.add(self.create_frame())
        self.window.show()

    def create_frame(self):
        vbox = Gtk().make_vbox()
        
        frame = Gtk().make_frame({'name':'New Profile', 'border':7})
        hbox_frame = Gtk().make_hbox()

        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.save_profile},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})
        
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(buttons, False, False, 0)

        image = Gtk().make_image({'stock':gtk.STOCK_DIALOG_AUTHENTICATION,
                                  'size':gtk.ICON_SIZE_DIALOG})
        
        hbox_frame.pack_start(image, True, True, 25)

        vbox_lab = Gtk().make_vbox()
        label_names = ['Id', 'Full Name', 'E-Mail', 'Password']
        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_lab.pack_start(label_dict[i], True, True, 0) for i in label_names]
        hbox_frame.pack_start(vbox_lab, True, True, 0)

        vbox_ent = Gtk().make_vbox()
        entry_names = ['id', 'name', 'email', 'passwd']
        entrys = dict((i,Gtk().make_entry()) for i in entry_names)
        [vbox_ent.pack_start(entrys[i], False, False, 2) for i in entry_names]
        hbox_frame.pack_start(vbox_ent, True, True, 5)

        entrys['passwd'].set_visibility(False)
        entrys['passwd'].connect('focus-in-event', self.show_entry)
        entrys['passwd'].connect('focus-out-event', self.show_entry)

        frame.add(hbox_frame)
        
        self.entrys = entrys
        return vbox

    def show_entry(self, widget=None, data=None):
        if not widget.get_visibility():
            widget.set_visibility(True)
        else:
            widget.set_visibility(False)

    def save_profile(self, widget):
        new_profile = dict((i,self.entrys[i].get_text().decode()) for i in self.entrys)
        passwd = Encryption().basic_encode(new_profile['passwd'])
        safekey = Encryption()._gen_passphrase(15)
        passphrase = Encryption().AES_encrypt(new_profile['passwd'], safekey)
        
        profile_dict = {'profile':new_profile['id'],
                        'name':new_profile['name'],
                        'email':new_profile['email'],
                        'status':u'enable',
                        'passwd':passwd.decode(),
                        'passphrase':passphrase}

        result = Profiles().make(profile_dict)
        if result != False:
            self.close_window()
            msg = '%s was created successfully.' %(new_profile['id'])
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})
            [i('[Profile] %s' %(msg)) for i in self.callbacks]
        else:
            msg = '%s: is already exist.' %(new_profile['id'])
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})

    def close_window(self, widget=None, event=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
