#!/bin/bash

# get into the correct directory
DETECTEDDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DETECTEDDIR/../
GITDIR=`pwd`
BUILDDIR=$GITDIR  # we'll manipulate this later, depending on the coverage flag


# check for clean
if [ "$1" == "clean" ] ; then
    # clean up any build-created files
    echo "Cleaning..."
    rm -f changelog.gz
    rm -f packaging/tmp.list
    rm -f packaging/guinan.list
    rm -rf packaging/guinan/
    rm -rf linux-2.*
    rm -rf linux-3.*
    rm -rf macosx-10.*
    rm -rf epm*
    echo "Done."
    exit 0
fi





#create EPM .list file
# available from: http://fossies.org/unix/privat/epm-4.2-source.tar.gz
# md5sum 3805b1377f910699c4914ef96b273943

echo "Creating Package ..."
if [ -d guinan ]; then
  rm -rf guinan
fi

# first create guinan source folder
cd $BUILDDIR
tar -cf guinan.tar --exclude=packaging --exclude=epm* --exclude=logs/.gitignore --exclude=linux-* --exclude=macosx-* * > /dev/null 2>&1
mv guinan.tar packaging
cd $BUILDDIR/packaging
mkdir guinan
tar xf guinan.tar -C guinan > /dev/null 2>&1
rm guinan.tar

# tar changelog file
# first remove any old one
cd $BUILDDIR
gzip -9 -c changelog > changelog.gz

# now create new guinan.list file
if [ -f guinan.list ]; then
  rm guinan.list
fi


# get RENCI updates to EPM from repository
cd $BUILDDIR
RENCIEPM="epm42-renci.tar.gz"
rm -rf epm
rm -f $RENCIEPM
wget -nc ftp://ftp.renci.org/pub/irods/build/$RENCIEPM
tar -xf $RENCIEPM



# build EPM
cd $BUILDDIR/epm
echo "Configuring EPM"
set +e
./configure > /dev/null
if [ "$?" != "0" ] ; then
    exit 1
fi
echo "Building EPM"
make > /dev/null
if [ "$?" != "0" ] ; then
    exit 1
fi
set -e



# generate guinan.list file
cd $BUILDDIR
$BUILDDIR/epm/mkepmlist -u eirods -g eirods --prefix /var/lib/guinan packaging/guinan > packaging/tmp.list
cat packaging/guinan.list.template packaging/tmp.list > packaging/guinan.list



# build package
cd $BUILDDIR
if [ -f "/etc/redhat-release" ]; then # CentOS and RHEL and Fedora
  echo "Running EPM :: Generating RPM"
  $BUILDDIR/epm/epm -a noarch -f rpm guinan RPM=true packaging/guinan.list
elif [ -f "/etc/SuSE-release" ]; then # SuSE
  echo "Running EPM :: Generating RPM"
  $BUILDDIR/epm/epm -a noarch -f rpm guinan RPM=true packaging/guinan.list
elif [ -f "/etc/lsb-release" ]; then  # Ubuntu
  echo "Running EPM :: Generating DEB"
  $BUILDDIR/epm/epm -f deb guinan DEB=true packaging/guinan.list
elif [ -f "/usr/bin/sw_vers" ]; then  # MacOSX
  echo "Running EPM :: Generating MacOSX DMG"
  $BUILDDIR/epm/epm -f osx guinan packaging/guinan.list
fi
