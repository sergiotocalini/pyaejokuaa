#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gobject
import gtk
from License import LicenseWindow
from lib.Constructor import Gtk
from lib.Path import APP_NAME, APP_VERSION

class AboutWindow():
    def __init__(self, parent):
        self.parent = parent
        self.parent.set_sensitive(False)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('delete-event', self.close_window)
        self.window.realize()
        self.window.set_modal(True)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.set_screen(parent.get_screen())
        self.window.set_title('%s - About' %(APP_NAME))
        self.window.set_transient_for(parent)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
                
        self.window.add(self.create_frame())
        self.window.show()

    def create_frame(self):
        vbox = Gtk().make_vbox()

        frame = Gtk().make_frame({'border':7})
        vboxinfo = Gtk().make_vbox({'border':7})
        
        image = Gtk().make_image({'stock':gtk.STOCK_NETWORK,
                                  'size':gtk.ICON_SIZE_DIALOG})
        vboxinfo.pack_start(image, True, True, 5)

        labels = [{'name':'%s %s' %(APP_NAME, APP_VERSION), 'font':'sans 16',
                   'halign':0.5},
                  {'name':'Remote Access To Anywhere', 'halign':0.5},
                  {'name':'Distributed under GPLv3 license.', 'halign':0.5},
                  {'name':'Sergio Tocalini Joerg', 'halign':0.5}]
        label_dic = dict((i['name'],Gtk().make_label(i)) for i in labels)
        [vboxinfo.pack_start(label_dic[i['name']],True,False,3) for i in labels]

        url = {'name':'http://www.sergiotocalini.com.ar',
               'url':'http://www.sergiotocalini.com.ar'}
        url_button = Gtk().make_linkbutton(url)
        vboxinfo.pack_start(url_button, False, False, 5)
        frame.add(vboxinfo)
        
        button_list = [{'stock':gtk.STOCK_ABOUT, 'cmd':self.window_develop,
                        'label':'Creditos', 'sensitive':False},
                       {'stock':gtk.STOCK_EDIT, 'cmd':self.window_license,
                        'label':'Licencia'},
                       {'stock':gtk.STOCK_CANCEL,'cmd':self.close_window}]
        buttons = Gtk().make_buttonbar(button_list, {'border':7})
        
        vbox.pack_start(frame, True, True, 5)
        vbox.pack_start(buttons, True, True, 5)
        return vbox

    def window_license(self, widget=None, data=None):
        LicenseWindow(self.window)

    def window_develop(self, widget=None, data=None):
        # DeveloperWindow(self.window)
        print ('develop')

    def close_window(self, widget=None, data=None):
        self.window.hide()
        self.window.destroy()
        self.parent.set_sensitive(True)
