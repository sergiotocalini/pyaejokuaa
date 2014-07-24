#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
import gtk
import os
import pango
import sys
import webbrowser

class Gtk():
    def make_entry(self, options={}):
        options.setdefault('editable', True)
        options.setdefault('horz', -1)
        options.setdefault('lenght', -1)
        options.setdefault('sensitive', True)
        options.setdefault('text', '')
        options.setdefault('tooltip', '')
        options.setdefault('vert', -1)
        options.setdefault('visibility', True)
        entry = gtk.Entry()
        entry.set_editable(options['editable'])
        entry.set_max_length(options['lenght'])
        entry.set_sensitive(options['sensitive'])
        entry.set_size_request(options['horz'], options['vert'])
        entry.set_text(options['text'])
        entry.set_tooltip_text(options['tooltip'])
        entry.set_visibility(options['visibility'])
        entry.show()
        return entry

    def make_entry_buttons(self, hbox_options={}, entry_options={}, buttons={}):
        hbox = self.make_hbox(hbox_options)        
        entry = self.make_entry(entry_options)

        for i in buttons:
            if not i.has_key('args'):
                i['args'] = entry

        res = [self.make_button_image(i) for i in buttons]

        hbox.pack_start(entry, False, False)
        [hbox.pack_start(i, False, False) for i in res]
        return hbox, entry

    def make_label(self, options={}):
        options.setdefault('font', False)
        options.setdefault('halign', 0)
        options.setdefault('justify', True)
        options.setdefault('name', '')
        options.setdefault('valign', 0.5)
        label = gtk.Label(options['name'])
        label.set_alignment(options['halign'], options['valign'])
        label.set_justify(options['justify'])
        if options['font'] != False:
            label.modify_font(pango.FontDescription(options['font']))
        label.show()
        return label

    def make_toolbar(self, options={}):
        options.setdefault('border', 1)
        options.setdefault('orientation', gtk.ORIENTATION_HORIZONTAL)
        options.setdefault('style', gtk.TOOLBAR_BOTH)
        toolbar = gtk.Toolbar()
        toolbar.set_border_width(options['border'])
        toolbar.set_orientation(options['orientation'])
        toolbar.set_style(options['style'])
        toolbar.show()
        return toolbar

    def make_statusbar(self, options={}):
        statusbar = gtk.Statusbar()
        statusbar.show()
        return statusbar

    def make_frame(self, options={}):
        options.setdefault('border', 10)
        options.setdefault('horz', -1)
        options.setdefault('name', '')
        options.setdefault('vertz', -1)
        frame = gtk.Frame(options['name'])
        frame.set_border_width(options['border'])
        frame.set_size_request(options['horz'], options['vertz'])
        frame.show()
        return frame

    def make_notebook(self, options={}):
        notebook = gtk.Notebook()
        notebook.set_current_page(0)
        notebook.show()
        return notebook

    def make_notebook_tab(self, notebook, options={}):
        options.setdefault('name', '')
        options.setdefault('stock', gtk.STOCK_NEW)
        options.setdefault('spacing', 5)

        tab_box = Gtk().make_hbox(options)
        icon = Gtk().make_image(options)
        label = Gtk().make_label(options)
        tab_box.pack_start(icon, False, False, 2)
        tab_box.pack_start(label, False, True, 0)
        
        vbox = Gtk().make_vbox(options)
    
        page = notebook.append_page(vbox, tab_box)
        return page, vbox

    def make_event_box(self, options={}, cmd=None, args=None):
        label = self.make_label(options)
        event_box = gtk.EventBox()
        event_box.add(label)
        event_box.connect("button_press_event", cmd, args)
        event_box.show()
        return event_box

    def make_vbox(self, options={}):
        options.setdefault('border', 0)
        options.setdefault('homogeneous', False)
        options.setdefault('spacing', 0)
        vbox = gtk.VBox()
        vbox.set_border_width(options['border'])
        vbox.set_homogeneous(options['homogeneous'])
        vbox.set_spacing(options['spacing'])
        vbox.show()
        return vbox

    def make_hbox(self, options={}):
        options.setdefault('border', 0)
        options.setdefault('homogeneous', False)
        options.setdefault('spacing', 0)
        hbox = gtk.HBox()
        hbox.set_border_width(options['border'])
        hbox.set_homogeneous(options['homogeneous'])
        hbox.set_spacing(options['spacing'])
        hbox.show()
        return hbox

    def make_linkbutton(self, options={}):
        options.setdefault('name', '')
        options.setdefault('url', '')
        linkbutton = gtk.LinkButton(options['url'], options['name'])
        linkbutton.show()
        return linkbutton

    def make_radiobutton(self, options={}, cmd=None, args=None):
        options.setdefault('name', '')
        options.setdefault('parent', None)
        radio_button = gtk.RadioButton(options['parent'], options['name'])
        radio_button.connect("toggled", cmd, args)
        radio_button.show()
        return radio_button

    def make_spinner(self, adj, vert=-1, horz=55):
        spinner = gtk.SpinButton(adj, 0, 0)
        spinner.set_wrap(False)
        spinner.set_size_request(horz, vert)
        spinner.show()
        return spinner

    def make_checkbox(self, options={}):
        options.setdefault('label', '')
        options.setdefault('sensitive', True)
        options.setdefault('tooltip', '')
        checkbox = gtk.CheckButton()
        checkbox.set_label(options['label'])
        checkbox.set_sensitive(options['sensitive'])
        checkbox.set_tooltip_text(options['tooltip'])
        return checkbox

    def make_button(self, cmd, stock, args=None):
        button = gtk.Button(stock=stock)
        button.connect_object("clicked", cmd, args)
        button.show()
        return button

    def make_buttonbar(self, buttons, options={}):
        options.setdefault('border', 2)
        options.setdefault('layout', gtk.BUTTONBOX_END)
        options.setdefault('spacing', 2)
        bbox = gtk.HButtonBox()
        bbox.set_border_width(options['border'])
        bbox.set_layout(options['layout'])
        bbox.set_spacing(options['spacing'])
        bbox.show()
        res = [self.make_button_stock(i) for i in buttons]
        [bbox.add(i) for i in res]
        return bbox

    def make_button_stock(self, options):
        options.setdefault('label', None)
        options.setdefault('sensitive', True)
        options.setdefault('tooltip', '')
        options.setdefault('size', gtk.ICON_SIZE_BUTTON)
        [options.setdefault(o, None) for o in ['stock', 'cmd', 'args']]
        if options['stock'] != None:
            if options['label'] != None:
                button = gtk.Button()
                button.set_label(options['label'])
                button.set_image(self.make_image(options))
            else:
                button = gtk.Button(stock=options['stock'])
            button.connect_object("clicked", options['cmd'], options['args'])
            button.set_sensitive(options['sensitive'])
            button.set_tooltip_text(options['tooltip'])
            button.show()
            return button
        else:
            return None

    def make_button_image(self, options):
        options.setdefault('sensitive', True)
        options.setdefault('size', gtk.ICON_SIZE_MENU)
        options.setdefault('tooltip', '')
        [options.setdefault(o, None) for o in ['stock', 'cmd', 'args']]
        if options['stock'] != None:
            button = gtk.Button()
            button.add(self.make_image(options))
            button.connect('pressed', options['cmd'], options['args'])
            button.set_sensitive(options['sensitive'])
            button.set_tooltip_text(options['tooltip'])
            button.show()
            return button
        else:
            return None
                    
    def make_image(self, options={}):
        options.setdefault('size', gtk.ICON_SIZE_MENU)
        if options.has_key('stock'):
            image = gtk.Image()
            image.set_from_stock(options['stock'], options['size'])
            image.show()
            return image
        else:
            return None

    def make_expander(self, options={}):
        options.setdefault('args', None)
        options.setdefault('callback', None)
        options.setdefault('title', '')
        expander = gtk.Expander(options['title'])
        expander.connect("notify::expanded", options['callback'], options['args'])
        expander.show()
        return expander

    def textview_box(self, title=None, editable=True,
                     horz_policity=gtk.POLICY_AUTOMATIC,
                     vert_policity=gtk.POLICY_AUTOMATIC):
        scrolledwindow = gtk.ScrolledWindow()
        scrolledwindow.set_border_width(10)
        scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        scroll_vbox = self.make_vbox()
        scroll_vbox.pack_start(scrolledwindow, True, True)

        view = gtk.TextView()
        view.set_editable(editable)
        buffer_text = view.get_buffer()
        view.show()

        scrolledwindow.add(view)
        scrolledwindow.show()
        if title:
            frame = self.create_frames(title, border=0)
            frame.add(scroll_vbox)
            return frame, view
        else:
            return scroll_vbox, view

    def make_dialog(self, options={}):
        options.setdefault('action', gtk.FILE_CHOOSER_ACTION_OPEN)
        options.setdefault('buttons', (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        options.setdefault('default_response', gtk.RESPONSE_OK)
        options.setdefault('dirname', os.environ['HOME'])
        options.setdefault('filter', {'All':['*']})
        options.setdefault('overwrite', True)
        options.setdefault('position', gtk.WIN_POS_CENTER_ALWAYS)
        options.setdefault('shortcut', ['/tmp'])
        options.setdefault('title', 'Dialog')
        
        dialog = gtk.FileChooserDialog(title=options['title'],
                                       action=options['action'],
                                       buttons=options['buttons'])
        
        [dialog.add_shortcut_folder(i) for i in options['shortcut']]
        dialog.set_default_response(options['default_response'])
        dialog.set_position(options['position'])
        dialog.set_property('do-overwrite-confirmation', options['overwrite'])
        dialog.set_current_folder(options['dirname'])

        for i in options['filter']:
            filter_file = gtk.FileFilter()
            filter_file.set_name(i)
            [filter_file.add_pattern(x) for x in options['filter'][i]]
            dialog.add_filter(filter_file)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            file_select = dialog.get_filename()
            dialog.destroy()
            return file_select
        else:
            dialog.destroy()

    def make_message(self, options={}):
        if options.has_key('msg'):
            options.setdefault('buttons', gtk.BUTTONS_OK)
            options.setdefault('flags', gtk.DIALOG_MODAL)
            options.setdefault('parent', None)
            options.setdefault('title', '')
            options.setdefault('type', gtk.MESSAGE_INFO)
            
            msg = gtk.MessageDialog(options['parent'], options['flags'],
                                    options['type'], options['buttons'],
                                    options['msg'])
            msg.set_title(options['title'])

            if options['buttons'] == gtk.BUTTONS_OK:
                msg.run()
                msg.destroy()
            elif options['buttons'] == gtk.BUTTONS_YES_NO:
                question = msg.run()
                if question == gtk.RESPONSE_YES:
                    msg.destroy()
                    return True
                else:
                    msg.destroy()
                    return False
        else:
            return None

    def delete_question(self, text):
        msg = unicode('¿Desea borrar permanentemente << %s >> ?'%(text),'latin-1')
        title = 'Confirmation'
        question_dict = {'msg':msg.encode("utf-8"), 'title':title,
                         'buttons':gtk.BUTTONS_YES_NO,
                         'type':gtk.MESSAGE_QUESTION}
        return self.make_message(question_dict)

    def file_question(self, archive):
        if os.path.isfile(archive):
            msg = 'Ya existe el archivo << %s >> ¿Desea reemplazarlo?' %(archive)
            msg = unicode(msg, "latin-1")
            title = 'Confirmation'
            question_dict = {'msg':msg.encode("utf-8"), 'title':title,
                             'buttons':gtk.BUTTONS_YES_NO,
                             'type':gtk.MESSAGE_QUESTION}
            return self.make_message(question_dict)
        else:
            return False

    def open_url(self, widget=None, url="http://www.pyadminstocks.com.ar/"):
        return webbrowser.open(url)
