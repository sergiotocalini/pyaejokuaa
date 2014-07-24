#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gtk
import os
from datetime import datetime
from ProfilesAdd import ProfilesAddWindow
from lib.Controller import Encryption, Profiles
from lib.Constructor import Gtk
from lib.Path import APP_NAME, THEME_PATH

class LoginWindow():
    def __init__(self, parent=None, profile=None, callbacks=[]):
        self.parent = parent
        if self.parent:
            self.parent.hide()

        self._profile = profile

        self.callbacks = callbacks
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.window.set_resizable(False)
        self.window.connect('delete-event', self.close_window)
        self.window.set_title('%s - Login' %(APP_NAME))
        self.window.set_icon_from_file(os.path.join(THEME_PATH, 'users.png'))
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.realize()
        self.window.set_modal(True)

        self.window.add(self.create_frame(self._profile))
        self.window.show()

    def create_frame(self, profile=None):
        vbox = Gtk().make_vbox()

        frame = Gtk().make_frame({'border':7})
        hbox_frame = Gtk().make_hbox()

        button_list = [{'stock':gtk.STOCK_OK,'cmd':self.login},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})
        
        vbox.pack_start(frame, True, True, 0)
        vbox.pack_start(buttons, False, False, 0)

        vbox_frame = Gtk().make_vbox()
        
        hbox_form = Gtk().make_hbox({'border':15})
        image = Gtk().make_image({'stock':gtk.STOCK_DIALOG_AUTHENTICATION,
                                 'size':gtk.ICON_SIZE_DIALOG})
        hbox_form.pack_start(image, True, True, 5)

        vbox_lab = Gtk().make_vbox()
        label_names = ['Login', 'Password']
        label_dict = dict((i,Gtk().make_label({'name':i})) for i in label_names)
        [vbox_lab.pack_start(label_dict[i], True, True, 0) for i in label_names]
        hbox_form.pack_start(vbox_lab, True, True, 0)

        vbox_ent = Gtk().make_vbox()
        entry_names = ['login', 'passwd']
        entrys = dict((i,Gtk().make_entry()) for i in entry_names)
        [vbox_ent.pack_start(entrys[i], False, False, 2) for i in entry_names]
        hbox_form.pack_start(vbox_ent, True, True, 5)

        vbox_frame.pack_start(hbox_form, True, True, 0)

        hbox_event = Gtk().make_hbox()
        event_new = Gtk().make_event_box({'name':'New Profile', 'halign':0.5},
                                         self.window_profiles_add)
        # event_rec = Gtk().make_event_box('Reset Password', self.passwd_recovery)
        hbox_event.pack_start(event_new, True, True, 5)
        # hbox_event.pack_start(event_rec, True, True, 5)
        
        vbox_frame.pack_start(hbox_event, True, True, 5)

        if profile:
            entrys['login'].set_text(profile)
        entrys['passwd'].set_visibility(False)

        frame.add(vbox_frame)
        
        self.entrys = entrys
        return vbox

    def login(self, widget=None):
        profile = dict((i,self.entrys[i].get_text()) for i in self.entrys)
        if profile['login']:
            login = Encryption().basic_auth(profile['login'], profile['passwd'])
            if login == True:
                Profiles().modify({'profile':profile['login'],
                                   'last_access':datetime.now()})
                self.window.hide()
                self.window.destroy()
                [i(profile['login'], profile['passwd']) for i in self.callbacks]
            elif login == False:
                msg = 'The password are incorrect.'
                title = '%s - Information' %(APP_NAME)
                Gtk().make_message({'msg':msg, 'title':title})
            else:
                msg = 'The user does not exist or are disable.'
                title = '%s - Information' %(APP_NAME)
                Gtk().make_message({'msg':msg, 'title':title})
        else:
            msg = 'The form are empty.'
            title = '%s - Information' %(APP_NAME)
            Gtk().make_message({'msg':msg, 'title':title})

    def passwd_recovery(self, widget=None, event=None):
        print (dict((i,self.entrys[i].get_text()) for i in self.entrys))

    def window_profiles_add(self, widget=None, event=None, args=None):
        ProfilesAddWindow(self.window)

    def close_window(self, widget=None, event=None):
        self.window.hide()
        self.window.destroy()
        if self.parent:
            self.parent.show()
            self.parent.set_sensitive(True)
        else:
            gtk.main_quit()

