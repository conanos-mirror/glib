#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools, Meson
import os
import shutil
import platform

from conanos.build import config_scheme
class GLibConan(ConanFile):
    name = "glib"
    version = "2.58.1"
    description = "GLib provides the core application building blocks for libraries and applications written in C"
    url = "https://github.com/GNOME/glib"
    homepage = "https://github.com/GNOME/glib"
    license = "LGPL-2.1"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_pcre": [True, False]}
    default_options = "shared=True", "fPIC=True", "with_pcre=False"
    source_subfolder = "%s-%s"%(name,version)
    autotools = None
    requires = "zlib/1.2.11@conanos/stable"

    def configure(self):
        #if self.settings.os != 'Linux':
        #    raise Exception("GNOME glib is only supported on Linux for now.")
        del self.settings.compiler.libcxx

        if self.settings.os == 'Windows':
            if not self.options.shared:
                raise Exception("Glib doesn't support static libraries on Windows yet.")


    def requirements(self):
        if self.settings.os == 'Linux':
            if self.options.with_pcre:
                self.requires.add("pcre/8.41@bincraftres/stable")
            self.requires.add('libffi/3.3-rc0@conanos/stable')

        config_scheme(self)

    def build_requirements(self):
        if platform.system() == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        #extracted_dir = self.name + "-" + self.version
        #os.rename(extracted_dir, self.source_subfolder)
        self._create_extra_files()

        

    def _create_extra_files(self):
        with open(os.path.join(self.source_subfolder, 'gtk-doc.make'), 'w+') as fd:
            fd.write('EXTRA_DIST =\n')
            fd.write('CLEANFILES =\n')
        for file_name in ['README', 'INSTALL']:
            open(os.path.join(self.source_subfolder, file_name), 'w+')

    def build(self):

        prefix = os.path.abspath('package')

        with tools.chdir(self.source_subfolder):
            meson = Meson(self)
            
            defs = { 'prefix':prefix, 
                      #'libdir':'lib',
                      'libmount':'false', 'dtrace':'false', 'selinux': 'false',
                      'internal_pcre' : 'true' if self.options.with_pcre else 'false'
            }
            
            pkgconfigdir=os.path.abspath('~pkgconfig')
            
            if not os.path.exists(pkgconfigdir):
                os.makedirs(pkgconfigdir)

            for name in self.requires.keys():                
                rootd = self.deps_cpp_info[name].rootpath
                pc =  os.path.join(rootd,name +'.pc')
                new_pc = os.path.join(pkgconfigdir,name +'.pc')
                shutil.copy(pc,pkgconfigdir)
                tools.replace_prefix_in_pc_file(new_pc,rootd)
            pkg_config_paths=[pkgconfigdir]

            meson.configure(defs=defs,
                source_folder = self.source_subfolder,
                build_folder  = '~build',
                pkg_config_paths=pkg_config_paths )
            meson.build()
            self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        prefix = os.path.abspath('~install')
        bind   = os.path.join(prefix,'bin') 
        libd   = os.path.join(prefix,'lib') 
        incd   = os.path.join(prefix,'include') 
        pkgd   = os.path.abspath('package')

        self.copy(pattern="*.dll", dst="bin",  src=bind, keep_path=False)
        self.copy(pattern="*.pdb", dst="bin",  src=bind, keep_path=False)
        shutil.copytree(libd,'./package/lib')
        shutil.copytree(incd,'./package/include')
        self.copy(pattern="*.pc", dst=".",  src='./package/lib/pkgconfig', keep_path=False)
        shutil.rmtree('./package/lib/pkgconfig')


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
        self.cpp_info.includedirs.append(os.path.join('include', 'glib-2.0'))
        self.cpp_info.includedirs.append(os.path.join('lib', 'glib-2.0', 'include'))
