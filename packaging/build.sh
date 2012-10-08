#!/bin/bash
#requirements:
# EPM packager

command -v epm >/dev/null 2>&1 || { echo "EPM commands must be in PATH to package guinan. Aborting." >&2; exit 1; }

# get into the correct directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

#create EPM .list file
# available from: http://fossies.org/unix/privat/epm-4.2-source.tar.gz
# md5sum 3805b1377f910699c4914ef96b273943

echo "Creating Package ..."
if [ -d guinan ]; then
  rm -rf guinan
fi

# first create guinan source folder
cd ..
tar -cf guinan.tar --exclude=packaging * > /dev/null 2>&1
mv guinan.tar packaging
cd packaging
mkdir guinan
tar xf guinan.tar -C guinan > /dev/null 2>&1
rm guinan.tar

# now create new guinan.list file
if [ -f guinan.list ]; then
  rm guinan.list
fi

mkepmlist -u eirods -g eirods --prefix /var/lib/guinan guinan > tmp.list
cat guinan.list.template tmp.list > guinan.list
rm tmp.list

# build package
if [ -f "/etc/redhat-release" ]; then # CentOS and RHEL and Fedora
  echo "Running EPM :: Generating RPM"
  epm -a noarch -f rpm guinan RPM=true guinan.list
elif [ -f "/etc/SuSE-release" ]; then # SuSE
  echo "Running EPM :: Generating RPM"
  epm -a noarch -f rpm guinan RPM=true guinan.list
elif [ -f "/etc/lsb-release" ]; then  # Ubuntu
  echo "Running EPM :: Generating DEB"
  epm -a noarch -f deb guinan DEB=true guinan.list
elif [ -f "/usr/bin/sw_vers" ]; then  # MacOSX
  echo "TODO: generate package for MacOSX"
fi
