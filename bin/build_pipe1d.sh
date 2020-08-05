#!/bin/bash

usage() {
    # Display usage and quit
    echo "Build the PFS 1D pipeline." 1>&2
    echo "" 1>&2
    echo "Requires that the LSST pipeline has already been installed and setup." 1>&2
    echo "" 1>&2
    echo "Usage: $0 [-b <BRANCH>] -l -k [-t TAG] <PREFIX> <SOURCE> <STACK>" 1>&2
    echo "" 1>&2
    echo "    -b <BRANCH> : name of branch on PFS to install" 1>&2
    echo "    -l : limited install (w/o drp_1d)" 1>&2
    echo "    -k : skip test procedure" 1>&2
    echo "    -t TAG : tag name to apply" 1>&2
    echo "" 1>&2
    exit 1
}

# Parse command-line arguments
SERVER="gfarm"
BRANCH="master"
LIMITED=false
TAG="current"
SKIP=false
while getopts ":s:b:hlkt:" opt; do
    case "${opt}" in
        s)
            SERVER=${OPTARG}
            ;;
        b)
            BRANCH=${OPTARG}
            ;;
        l)
            LIMITED=true
            ;;
        k)
            SKIP=true
            ;;
        t)
            TAG=${OPTARG}
            ;;
        h | *)
            usage
            ;;
    esac
done

shift $((OPTIND-1))

PREFIX=$1
SOURCE=$2
STACK=$3
if [ -z "PREFIX" ] || [ -z "$SOURCE" ] || [ -z "$STACK" ] || [ -n "$4" ]; then
    usage
fi

cd $PREFIX
TARGET="$(pwd)"


if [ "$SERVER" = "gfarm" ]; then
    if [ "$LIMITED" = false ]; then
        cd $SOURCE/drp_1d
        git checkout $BRANCH
        git pull
        cd build
        make clean
        cmake3 .. -DCMAKE_INSTALL_PREFIX=$STACK -DMISSING_THIRDPARTIES=boost
        make -j 4  2>&1 | tee $TARGET/build_pfs_pipe1d_library.log
        make install
        cd ..
        python setup.py install
        cd build
        if [ "$SKIP" = false ]; then
            make test
        fi
    fi
    cd $SOURCE/drp_1dpipe
    git checkout $BRANCH
    git pull
    python setup.py install 2>&1 | tee $TARGET/build_pfs_pipe1d_client.log
    if [ "$SKIP" = false ]; then
        pytest
    fi
fi

echo ""
echo "All done."
echo ""

