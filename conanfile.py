from conans import ConanFile, CMake, tools
import os
import platform

class JsoncConan(ConanFile):
    name = 'jsonc'

    source_version = '0.15'
    source_fullversion = '0.15-20200726'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
        'vuoutils/1.2@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-jsonc'
    license = 'https://github.com/json-c/json-c/blob/master/COPYING'
    description = 'Construct JSON objects in C, output them as JSON formatted strings and parse JSON formatted strings back into the C representation of JSON objects'
    source_dir = 'json-c-json-c-%s' % source_fullversion

    build_dir = '_build'
    install_dir = '_install'

    libs = {
        'json-c': 5,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/json-c/json-c/archive/json-c-%s.tar.gz' % self.source_fullversion,
                  sha256='4ba9a090a42cf1e12b84c64e4464bb6fb893666841d5843cc5bef90774028882')

        self.run('mv %s/COPYING %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        import VuoUtils

        cmake = CMake(self)

        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER']   = '%s/bin/clang'   % self.deps_cpp_info['llvm'].rootpath
        cmake.definitions['CMAKE_C_FLAGS'] = '-Oz'
        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_INSTALL_PREFIX'] = '%s/%s' % (os.getcwd(), self.install_dir)
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['BUILD_SHARED_LIBS'] = 'ON'
        cmake.definitions['BUILD_STATIC_LIBS'] = 'OFF'
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='../%s' % self.source_dir,
                            build_dir='.')
            cmake.build()
            cmake.install()

        with tools.chdir('%s/lib' % self.install_dir):
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include' % self.install_dir, dst='include')
        self.copy('libjson-c.%s' % libext, src='%s/lib' % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['json-c']
