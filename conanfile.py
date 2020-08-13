#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
import shutil
import os


class LibmodbusConan(ConanFile):
    name = "libmodbus"
    license = "LGPL-2.1"
    url = "https://github.com/sintef-ocean/conan-libmodbus"
    homepage = "http://libmodbus.org"
    author = "SINTEF Ocean"
    description = \
        "libmodbus is a free software library to send/receive data with a "\
        "device which respects the Modbus protocol."
    topics = ("modbus", "communication", "protocol")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    exports_sources = ["extra/*", "CMakeLists.txt"]
    source_subfolder = "libmodbus"
    build_subfolder = "build_subfolder"

    _env_build = None
    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self.source_subfolder,
                build_folder=self.build_subfolder)
        return self._cmake

    def _configure_env_build(self):
        if self._env_build:
            return self._env_build
        self._env_build = AutoToolsBuildEnvironment(self)
        self._env_build.fpic = True
        return self._env_build

    def _buildtool_install(self):
        if self._cmake:
            self._cmake.install()
        if self._env_build:
            self._env_build.install()

    def set_version(self):
        self.version = tools.load(
            self.recipe_folder + os.sep + "version.txt").strip()

    def source(self):
        self.run("git clone --depth 1 -b v{0} "
                 "https://github.com/stephane/libmodbus.git"
                 .format(self.version))

    def build(self):
        if self.settings.compiler == "Visual Studio":
            shutil.move(self.source_folder + "/CMakeLists.txt",
                        self.source_folder + "/{}/CMakeLists.txt"
                        .format(self.source_subfolder))
            shutil.move(self.source_folder + "/extra/win_config.h",
                        self.source_folder + "/{}/config.h"
                        .format(self.source_subfolder))
            shutil.move(self.source_folder + "/extra/project-config.cmake.in",
                        self.source_folder + "/{}/project-config.cmake.in"
                        .format(self.source_subfolder))
            tools.patch(patch_file=self.source_folder + "/extra/modbus.patch",
                        base_path=self.source_subfolder)
            cmake = self._configure_cmake()
            cmake.build()
        else:
            config_args=[]
            if self.options.shared:
                config_args.extend(["--enable-shared","--disable-static"])
            else:
                config_args.extend(["--enable-static","--disable-shared"])
            config_args.append("--prefix={}".format(self.package_folder))
            env_build = self._configure_env_build()
            with tools.environment_append(env_build.vars):
                with tools.chdir(os.path.join(self.source_folder, self.source_subfolder)):
                    self.run("./autogen.sh")
            if self.settings.arch != "x86_64" and self.settings.arch != "x86":
                config_host="{}".format(self.settings.arch)
            else:
                config_host=False
            env_build.configure( \
                    configure_dir=os.path.join(self.source_folder, self.source_subfolder), \
                    args=config_args, \
                    host=config_host)
            env_build.make()

    def package(self):
        self._buildtool_install()
        self.copy("COPYING.LESSER", dst="licenses", src=self.source_subfolder,
                  ignore_case=True, keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ["modbus"]
            else:
                self.cpp_info.libs = ["libmodbus", "ws2_32"]
                self.cpp_info.defines = ["LIBMODBUS_STATICBUILD"]
            if self.settings.build_type == "Debug":
                self.cpp_info.libs[0] += '_d'
        else:
            self.cpp_info.libs = ["modbus"]
        self.cpp_info.includedirs = ["include", "include/modbus"]
        self.cpp_info.name = "Libmodbus"

    def configure(self):
        del self.settings.compiler.libcxx
