#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools, Meson
import os


class GLibConan(ConanFile):
    name = "glib"
    version = "2.57.1"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://github.com/bincrafters/conan-glib"
    homepage = "https://github.com/GNOME/glib"
    license = "LGPL-2.1"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_pcre": [True, False]}
    default_options = "shared=True", "fPIC=True", "with_pcre=False"
    source_subfolder = "source_subfolder"
    autotools = None
    requires = "libffi/3.3-rc0@conanos/dev","zlib/1.2.11@conanos/dev"

    def configure(self):
        if self.settings.os != 'Linux':
            raise Exception("GNOME glib is only supported on Linux for now.")
        del self.settings.compiler.libcxx

    def requirements(self):
        if self.options.with_pcre:
            self.requires.add("pcre/8.41@bincraftres/stable")

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
        self._create_extra_files()

    def _create_extra_files(self):
        with open(os.path.join(self.source_subfolder, 'gtk-doc.make'), 'w+') as fd:
            fd.write('EXTRA_DIST =\n')
            fd.write('CLEANFILES =\n')
        for file_name in ['README', 'INSTALL']:
            open(os.path.join(self.source_subfolder, file_name), 'w+')

    def build(self):
        with tools.chdir(self.source_subfolder):
            meson = Meson(self)
            _defs = { 'prefix':'%s/builddir/install'%(os.getcwd()), 'libdir':'lib',
                      'libmount':'false', 'dtrace':'false', 'selinux': 'false',
                      'internal_pcre' : 'true' if self.options.with_pcre else 'false'
            }
            meson.configure(
                defs=_defs,
                source_dir = '%s'%(os.getcwd()),
                build_dir= '%s/builddir'%(os.getcwd()),
                pkg_config_paths=['%s/lib/pkgconfig'%(self.deps_cpp_info["libffi"].rootpath),
                                  '%s/lib/pkgconfig'%(self.deps_cpp_info["zlib"].rootpath)]
                )
            meson.build(args=['-j2'])
            self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir/install"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.cpp_info.includedirs.append(os.path.join('include', 'glib-2.0'))
        self.cpp_info.includedirs.append(os.path.join('lib', 'glib-2.0', 'include'))
