#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gtk

class System_Tray():
    def __init__(self, window):
        self.main_window = window
        
    def make(self):
        icon = gtk.StatusIcon()
        icon.set_from_stock(gtk.STOCK_INFO)
        icon.connect("activate", self.left_click)

        return icon

    def left_click(self, widget=None):
        if self.main_window.is_active():
            self.main_window.hide()
        else:
            self.main_window.present()

if __name__ == "__main__":
    print "This is a plugin you can't run it without pyAeJokuaa."
