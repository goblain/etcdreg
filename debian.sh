#!/bin/bash

[ -d build ] && rm -rf build
mkdir -p build/src
cp -r bin build/src/
cp -r etcdreg build/src/
cp setup.py build/src/
cd build/src
# sudo apt-get install python-stdeb

python setup.py --command-packages=stdeb.command debianize --suite=trusty --build-depends='python-setuptools (>= 0.6b3), python-all (>= 2.6.0-1), debhelper (>= 7.4.3)'
python setup.py sdist
sed -i "s/Build-Depends: .*/Build-Depends: python-setuptools (>= 0.6b3), python-all (>= 2.6.0-1), debhelper (>= 7.4.3)/" debian/control
python setup.py debbuild
python setup.py debuploadppa

#mv dist/etcdreg-0.1.1.tar.gz ../etcdreg_0.1.1.orig.tar.gz
#dpkg-buildpackage -S -sa -kgoblin@pentex.pl
#cd ..
#dput -l ppa:goblain/devops etcdreg_0.1.1-*_source.changes
