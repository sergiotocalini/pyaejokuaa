#!/usr/bin/env python
import gtk
import run

class Base():
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        vbox = gtk.VBox()

        notebook = gtk.Notebook()
        notebook.show()

        Admin = run.Initial("negro", notebook)

        frame = Admin.initial("usehux100", "sshtousehux100 tocalse1")

        vbox.pack_start(notebook, True, True, 1)
        vbox.show()
        
        self.window.add(vbox)
        self.window.show()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    base = Base()
    base.main()
