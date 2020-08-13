#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake
import os


class LibmodbusTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake_find_package"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.lib", dst="lib", src="lib")
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        if self.settings.os == "Windows":
            path = self.build_folder + os.sep \
                + str(self.settings.build_type) + os.sep
            if self.options["libmodbus"].shared:
                runcwd = self.build_folder + os.sep \
                    + "bin" + os.sep
            else:
                runcwd = None
            self.run("%sexample.exe" % path, cwd=runcwd)
        else:
            self.run(".%sexample" % os.sep)
