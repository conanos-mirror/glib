#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools, Meson
import os
import shutil
import platform
import sys

from conanos.build import config_scheme
class GLibConan(ConanFile):
    name = "glib"
    version = "2.58.1"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://github.com/GNOME/glib"
    homepage = "https://github.com/GNOME/glib"
    license = "LGPL-2.1"
    exports = ["COPYING"]
    generators = "visual_studio", "gcc"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_pcre": [True, False]}
    default_options = { 'shared': False, 'fPIC': True, 'with_pcre' : False }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    

    def requirements(self):
        self.requires.add("zlib/1.2.11@conanos/stable")
        self.requires.add("libffi/3.299999@conanos/stable")

        config_scheme(self)

    def configure(self):
        del self.settings.compiler.libcxx


    #def requirements(self):
    #    if self.settings.os == 'Linux':
    #        if self.options.with_pcre:
    #            self.requires.add("pcre/8.41@bincraftres/stable")
    #        #self.requires.add('libffi/3.3-rc0@conanos/stable')

    #    config_scheme(self)

    def source(self):
        url_ = 'https://github.com/GNOME/glib/archive/{version}.tar.gz'.format(version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["zlib","libffi"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        meson = Meson(self)
        meson.configure(defs={'prefix' : prefix},
                        source_dir=self._source_subfolder, build_dir=self._build_subfolder,
                        pkg_config_paths=pkg_config_paths)
        meson.build()
        self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.cpp_info.includedirs.append(os.path.join('include', 'glib-2.0'))
        self.cpp_info.includedirs.append(os.path.join('lib', 'glib-2.0', 'include'))
