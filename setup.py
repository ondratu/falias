from distutils.core import setup, Command
from distutils.command.install_data import install_data
from distutils.dir_util import remove_tree
from distutils import log

from os import path, makedirs, walk, environ
from shutil import copyfile
from subprocess import call
from sys import version_info

if version_info[0] >= 3:
    from io import FileIO
    file = FileIO

from falias import __version__
environ.update({'PYTHONPATH': 'falias'})


def find_data_files(directory, targetFolder=""):
    def skip(name):
        return (name[0] != '.' and name[-1] != '~')

    rv = []
    for root, dirs, files in walk(directory):
        if targetFolder:
            rv.append((targetFolder,
                       list(root+'/'+f for f in files if skip(f))))
        else:
            rv.append((root,
                       list(root+'/'+f for f in files if skip(f))))
    log.info(str(rv))
    return rv


class build_html(Command):
    description = "build html documentation, need jinja24doc >= 1.1.0"
    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build.build-base')"),
        ('html-temp=', 't',
         "temporary documentation directory")
        ]

    def initialize_options(self):
        self.build_base = None
        self.html_temp = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_base', 'build_base'))
        if self.html_temp is None:
            self.html_temp = path.join(self.build_base, 'html')

    def run(self):
        log.info("building html docmuentation")
        if self.dry_run:
            return

        if not path.exists(self.html_temp):
            makedirs(self.html_temp)
        if call(['jinja24doc', '-v', 'readme.html', 'doc'],
                stdout=file(self.html_temp + '/index.html', 'w')):
            raise IOError(1, 'jinja24doc failed')

        if call(['jinja24doc', '-v', 'reference.html', 'doc'],
                stdout=file(self.html_temp + '/api.html', 'w')):
            raise IOError(1, 'jinja24doc failed')

        if call(['jinja24doc', '-v', 'licence.html', 'doc'],
                stdout=file(self.html_temp + '/licence.html', 'w')):
            raise IOError(1, 'jinja24doc failed')
        copyfile('doc/style.css', self.html_temp + '/style.css')


class clean_html(Command):
    description = "clean up temporary files from 'build_html' command"
    user_options = [
        ('build-base=', 'b',
         "base build directory (default: 'build-html.build-base')"),
        ('html-temp=', 't',
         "temporary documentation directory")
        ]

    def initialize_options(self):
        self.build_base = None
        self.html_temp = None

    def finalize_options(self):
        self.set_undefined_options('build_html',
                                   ('build_base', 'build_base'),
                                   ('html_temp', 'html_temp'))

    def run(self):
        if path.exists(self.html_temp):
            remove_tree(self.html_temp, dry_run=self.dry_run)
        else:
            log.warn("'%s' does not exist -- can't clean it", self.html_temp)


class install_html(install_data):
    description = "install html documentation"
    user_options = install_data.user_options + [
        ('build-base=', 'b',
         "base build directory (default: 'build-html.build-base')"),
        ('html-temp=', 't',
         "temporary documentation directory"),
        ('skip-build', None, "skip the build step"),
    ]

    def initialize_options(self):
        self.build_base = None
        self.html_temp = None
        self.skip_build = None
        install_data.initialize_options(self)

    def finalize_options(self):
        self.set_undefined_options('build_html',
                                   ('build_base', 'build_base'),
                                   ('html_temp', 'html_temp'))
        self.set_undefined_options('install',
                                   ('skip_build', 'skip_build'))
        install_data.finalize_options(self)

    def run(self):
        if not self.skip_build:
            self.run_command('build_html')
        self.data_files = find_data_files(self.html_temp,
                                          'share/doc/poorwsgi/html')
        install_data.run(self)


class PyTest(Command):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        self.pytest_args = []

    def finalize_options(self):
        pass

    def run(self):
        print (self.pytest_args)
        import pytest
        errno = pytest.main(self.pytest_args)
        raise SystemExit(errno)


def _setup(**kwargs):
    # if version_info[0] == 2 and version_info[1] < 7:
    #    kwargs['install_requires'] = ['ordereddict >= 1.1']
    setup(**kwargs)


def doc():
    with open('README.rst', 'r') as readme:
        return readme.read().strip()

setup_kwargs = {
    'name':             "Falias",
    'version':          __version__,
    'description':      "Lightweight support python library",
    'author':           "Ondrej Tuma",
    'author_email':     "mcbig@zeropage.cz",
    'url':              "http://falias.zeropage.cz/",
    'packages':         ['falias'],
    'data_files':       [('share/doc/falias', ['LICENCE', 'README.rst']), ],
    'license':          "BSD",
    'long_description': doc(),
    'classifiers':      [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Natural Language :: Czech",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    'cmdclass':         {'test': PyTest,
                         'build_html': build_html,
                         'clean_html': clean_html,
                         'install_html': install_html},
}

_setup(**setup_kwargs)
