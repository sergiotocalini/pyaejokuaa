#!/usr/bin/env python
import os
import sys
# from configobj import ConfigObj
from Path import APP_NAME, PLUG_PATH, PLUG_FILE, _get_pluginFile

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def _check_plugin_healthy(self, plugin_dir):
        if 'PKG-INFO' in os.listdir(plugin_dir):
            print True

    def _find_available_plugins(self):
        plugin_dic = {}
        for i in PLUG_PATH:
            for x in [z for z in os.listdir(i) if not z.startswith('.')]:
                plug_dir = os.path.join(i, x)
                if os.path.isdir(plug_dir) and not plugin_dic.has_key(x):
                        plugin_dic[x] = plug_dir
        return plugin_dic

    def _update_pluginFile(self, plugin_dic):
        pluginFile = _get_pluginFile(PLUG_FILE)
        for i in plugin_dic:
            plugin_info = self._load_plugin_information(plugin_dic[i])
            if not pluginFile[plugin_info['category']].has_key(i):
                pluginFile[plugin_info['category']][i] = 'inactive'
        config.write()

    def _load_plugin_information(self, plugin_dir):
        configfile = ConfigObj(os.path.join(plugin_dir,'PKG-INFO'))
        dict_infoplug = {'name':configfile['Name'],
                         'category':configfile['Category'],
                         'version':configfile['Version'],
                         'summary':configfile['Summary'],
                         'web':configfile['Home-page'],
                         'author':configfile['Author'],
                         'email':configfile['Author-email'],
                         'license':configfile['License'],
                         'descrip':configfile['Description'],
                         'platform':configfile['Platform']}
        
        return dict_infoplug

    def install_plugin(self, plugin_name):
        list_files = Gtk().list_tar_files(install_file)
        if list_files:
            for i in list_files:
                if i.endswith('PKG-INFO'):
                    pkg_info = path + i
                    valite_pkg = True

        if valite_pkg:
            result = Gtk().extract_tar_files(install_file, path)
            if result:
                return True, pkg_info
            else:
                return False, False

    def analist_plugin_file(self, plugin_file, dict_plug):
        plug_configfile = ConfigObj(plugin_file)
        for i in plug_configfile:
            dict_plug[i] = []
            for x in plug_configfile[i]:
                dict_plug[i].append(x)
            dict_plug[i].sort()
        return dict_plug

    def load_plugins_list(self, treeview):
        dict_plug = {}
        dict_plug = self.analist_plugin_file(sys_plug, dict_plug)
        dict_plug = self.analist_plugin_file(user_plug, dict_plug)

        plugins = []
        for i in dict_plug:
            for x in dict_plug[i]:
                plugins.append(x)
        plugins.sort()

        model = treeview.get_model()
        model.clear()

        for i in plugins:
            plug_info = self.load_plugin_information(i, sys_plug, user_plug)
            name = str(plug_info['name'])
            version = '\t' + str(plug_info['version'])
            descrip = '\n' + str(plug_info['summary'])
            model.append(None, (False, name + version + descrip,
                                plug_info))

    def load_install(self, widget, plug_local=True):
        sys_plug, user_plug = self.search_configfile()
        if plug_local:
            plug_conf = user_plug
            plug_dir = user_plug.replace('plugins.conf', '')
        else:
            plug_conf = sys_plug
            plug_dir = sys_plug.replace('plugins.conf', '')

        dict_filters = {'tar':['*.tar'], 'tar.bz':['*.tar.bz'],
                        'tar.bz2':['*.tar.bz2']}
        install_file = Gtk().open_file_dialog(None, 'Install', dict_filters)
        if install_file:
            install_result, pkg_info = self.install_plugin(install_file,
                                                           plug_dir)
            if install_result:
                result = self.add_plugin(pkg_info, plug_conf)

