#!/usr/bin/env python
import gtk
import controller

class Initial():
    def __init__(self, session, notebook):
        self.Admin_Terminal = controller.Admin_Terminal()
        self.Admin_Notebook = controller.Admin_Notebook()
        self.data_tab = []
        self.session = session
        self.main_notebook = notebook
        self.tab_notebook = self.Admin_Notebook.create_notebook()

    def initial(self, tab_name=None, args=None):
        frame = self.verify_mainframe(self.main_notebook)
        tab_box = self.create_mainframe()

        if tab_name:
            self.create_tab(tab_box, tab_name, args)
        else:
            self.create_tab(tab_box, "Terminal", args)

        frame.add(tab_box)
        return frame

    def verify_mainframe(self, notebook, name=None):
        frame = self.check_notebook(notebook)
        if not frame:
            if not name:
                frame = gtk.Frame("")
                label = gtk.Label("Plugin: hesapea")
            else:
                frame = gtk.Frame("")
                label = gtk.Label(name)
            frame.show()
            label.show()
            page = notebook.append_page(frame, label)
            notebook.set_current_page(page)
        return frame

    def check_notebook(self, notebook):
        children = notebook.get_children()
        for i in children:
            if i.get_label() == "Plugin: hesapea":
                print "already exist."
                return i
        return False

    def create_mainframe(self):
        vbox = gtk.VBox()
        vbox.show()
        toolbar_box = gtk.HBox()
        toolbar_box.show()
        handlebox = gtk.HandleBox()
        toolbar = gtk.Toolbar()
        toolbar.set_orientation(gtk.ORIENTATION_HORIZONTAL)
        toolbar.set_style(gtk.TOOLBAR_BOTH)
        toolbar.set_border_width(1)
        toolbar.show()
        new_icon = gtk.Image()
        new_icon.set_from_stock(gtk.STOCK_ADD,
                                gtk.ICON_SIZE_BUTTON)
        new_icon.show()
        pref_icon = gtk.Image()
        pref_icon.set_from_stock(gtk.STOCK_PREFERENCES,
                                 gtk.ICON_SIZE_BUTTON)
        pref_icon.show()
        quit_icon = gtk.Image()
        quit_icon.set_from_stock(gtk.STOCK_QUIT,
                                 gtk.ICON_SIZE_BUTTON)
        quit_icon.show()
        toolbar.append_item("New", "Open a new terminal tab", "Private",
                            new_icon, self.open_new_tab_term)
        toolbar.append_space()
        toolbar.append_item("Preferences", "Preferences", "Private",
                            pref_icon, None)
        toolbar.append_space()
        toolbar.append_item("Quit", "Quit", "Private",
                            quit_icon, self.close_plugin)
        handlebox.add(toolbar)
        handlebox.show()
        toolbar_box.pack_start(handlebox, True, True, 0)

        vbox.pack_start(toolbar_box, False, False, 0)
        vbox.pack_start(self.tab_notebook, True, True, 2)
        return vbox

    def create_tab(self, vbox, tab_name, args=None):
        tab_frame, tab_label = self.Admin_Notebook.create_frame(tab_name, 5)
        page = self.Admin_Notebook.append_tab(self.tab_notebook, tab_frame,
                                              tab_label)
        vbox = gtk.VBox()
        vbox.show()
        box_terminal = self.create_terminal(args)
        button_close = gtk.Button(stock="gtk-close")
        button_close.connect("clicked", self.close_tab)
        button_close.show()
        button_bar = gtk.HButtonBox()
        button_bar.set_border_width(2)
        button_bar.set_layout(gtk.BUTTONBOX_END)
        button_bar.set_spacing(2)
        button_bar.show()
        button_bar.add(button_close)
        vbox.pack_start(box_terminal, True, True, 2)
        vbox.pack_start(button_bar, False, False, 2)
        tab_frame.add(vbox)

    def create_terminal(self, args=None):
        hbox = gtk.HBox()
        hbox.set_border_width(5)
        hbox.show()
        terminal = self.Admin_Terminal.create_terminal(self.close_tab, args)
        self.Admin_Terminal.load_preference(terminal, self.session)
        hbox.pack_start(terminal, True, True, 2)
        return hbox

    def open_new_tab_term(self, widget=None):
        tab_box = self.tab_notebook.get_children()[0]
        self.create_tab(tab_box, "Terminal")

    def close_tab(self, widget=None):
        page = self.tab_notebook.get_current_page()
        self.tab_notebook.remove_page(page)
        self.tab_notebook.queue_draw_area(1,1,1,1)

        if not self.tab_notebook.get_children():
            self.close_plugin()

    def close_plugin(self, widget=None):
        page = self.main_notebook.get_current_page()
        self.main_notebook.remove_page(page)
        self.main_notebook.queue_draw_area(1,1,1,1)
