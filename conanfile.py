from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
import platform

class JsoncConan(ConanFile):
    name = 'jsonc'

    source_version = '0.12'
    source_fullversion = '0.12-20140410'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://github.com/vuo/conan-jsonc'
    license = 'https://github.com/json-c/json-c/blob/master/COPYING'
    description = 'Construct JSON objects in C, output them as JSON formatted strings and parse JSON formatted strings back into the C representation of JSON objects'
    source_dir = 'json-c-json-c-%s' % source_fullversion
    build_dir = '_build'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/json-c/json-c/archive/json-c-%s.tar.gz' % self.source_fullversion,
                  sha256='99304a4a633f1ee281d6a521155a182824dd995139d5ed6ee5c93093c281092b')

        self.run('mv %s/COPYING %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

    def build(self):
        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            autotools = AutoToolsBuildEnvironment(self)

            # The LLVM/Clang libs get automatically added by the `requires` line,
            # but this package doesn't need to link with them.
            autotools.libs = ['c++abi']

            autotools.flags.append('-Oz')
            autotools.flags.append('-Wno-error')

            if platform.system() == 'Darwin':
                autotools.flags.append('-mmacosx-version-min=10.10')
                autotools.link_flags.append('-Wl,-headerpad_max_install_names')
                autotools.link_flags.append('-Wl,-install_name,@rpath/libjson-c.dylib')

            env_vars = {
                'CC' : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX': self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
            }
            with tools.environment_append(env_vars):
                autotools.configure(configure_dir='../%s' % self.source_dir,
                                    build=False,
                                    host=False,
                                    args=['--quiet',
                                          '--prefix=%s' % os.getcwd()])
                autotools.make(args=['--quiet'])
                autotools.make(target='install', args=['--quiet'])

            if platform.system() == 'Linux':
                patchelf = self.deps_cpp_info['patchelf'].rootpath + '/bin/patchelf'
                self.run('%s --set-soname libjson-c.so lib/libjson-c.so' % patchelf)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.copy('*.h', src='%s/include' % self.build_dir, dst='include')
        self.copy('libjson-c.%s' % libext, src='%s/lib' % self.build_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['json-c']
