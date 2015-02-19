from setuptools import setup
from setuptools import Command
import os
from pprint import pprint

execfile('etcdreg/version.py')

class DebBuild(Command):
  description = "build debian package for ppa upload"
  user_options = []
  def initialize_options(self):
    pprint(__version__)
  def finalize_options(self):
    self.cwd = os.getcwd()
  def run(self):
    assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
    os.system('mv dist/etcdreg-'+__version__+'.tar.gz ../etcdreg_'+__version__+'.orig.tar.gz')
    os.system('dpkg-buildpackage -S -sa -kgoblin@pentex.pl')

class DebUploadppa(Command):
  description = "upload debian package to ppa"
  user_options = []
  def initialize_options(self):
    self.cwd = None
  def finalize_options(self):
    self.cwd = os.getcwd()
  def run(self):
    assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
    os.system('cd ..; dput -l ppa:goblain/devops etcdreg_'+__version__+'-*_source.changes')

setup(name='etcdreg',
      version=__version__,
      description='Etcd service registrator',
      url='http://github.com/goblain/etcdreg',
      author='Radoslaw Goblin Pieczonka',
      author_email='goblin@pentex.pl',
      license='MIT',
      packages=['etcdreg'],
      scripts=['bin/etcdreg'],
      classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT",
      ],
      cmdclass = {
        'debbuild': DebBuild,
        'debuploadppa': DebUploadppa
      },
      zip_safe=False
)

