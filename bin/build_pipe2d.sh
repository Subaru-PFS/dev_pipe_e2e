#!/bin/bash

usage() {
    # Display usage and quit
    echo "Build the PFS 2D pipeline." 1>&2
    echo "" 1>&2
    echo "Requires that the LSST pipeline has already been installed and setup." 1>&2
    echo "" 1>&2
    echo "Usage: $0 [-s <SERVER>] [-b <BRANCH>] [-l] [-t TAG] <PREFIX> <SOURCE>" 1>&2
    echo "" 1>&2
    echo "    -s <SERVER> : name of server" 1>&2
    echo "    -b <BRANCH> : name of branch on PFS to install" 1>&2
    echo "    -l : limited install (w/o drp_stella, pfs_pipe2d)" 1>&2
    echo "    -t <TAG> : tag name to apply" 1>&2
    echo "" 1>&2
    exit 1
}

# Parse command-line arguments
SERVER="gfarm"
BRANCH="master"
LIMITED=false
TAG="current"
PREFIX=""
SOURCE=""
while getopts ":s:b:hlt:" opt; do
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
if [ -z "PREFIX" ] || [ -z "$SOURCE" ] || [ -n "$3" ]; then
    usage
fi

if [ "$SERVER" = "gfarm" ]; then
    cd $PREFIX
    setup pipe_drivers
    $SOURCE/build_pfs.sh -b $BRANCH -t $TAG 2>&1 | tee build_pfs_pipe2d.log
elif [ "$SERVER" = "docker" ]; then
    cd $PREFIX
    setup pipe_drivers
    $SOURCE/build_pfs.sh -b $BRANCH -t $TAG 2>&1 | tee build_pfs_pipe2d.log
fi

echo ""
echo "All done."
echo ""

