#!/bin/bash

usage() {
    # Display usage and quit
    echo "Test the PFS pipeline end-to-end process." 1>&2
    echo "" 1>&2
    echo "Usage: $0 [-r <RERUN>] [-d DIRNAME] [-t <TAG1D>] [-c CORES] <PREFIX>" 1>&2
    echo "" 1>&2
    echo "    -r <RERUN> : rerun name to use (default: 'integration')" 1>&2
    echo "    -d <DIRNAME> : directory name to give data repo (default: 'INTEGRATION')" 1>&2
    echo "    -t <TAG1D> : directory name to put 1D results (default: pipe1d_workdir)" 1>&2
    echo "    -c <CORES> : number of cores to use (default: 1)" 1>&2
    echo "    -G : don't clone or update from git" 1>&2
    echo "    -k : skip 2D procedure" 1>&2
    echo "    <PREFIX> : directory under which to operate" 1>&2
    echo "" 1>&2
    exit 1
}

# Parse command-line arguments
SERVER="gfarm"
RERUN="integration"  # Rerun name to use
TARGET="INTEGRATION"  # Directory name to give data repo
TAG1D="pipe1d_workdir" # Directory name for 1D results
SKIP2D=false
CORES=1  # Number of cores to use
USE_GIT=true # checkout/update from git
while getopts ":c:t:d:Gkr:" opt; do
    case "${opt}" in
        c)
            CORES=${OPTARG}
            ;;
        d)
            TARGET=${OPTARG}
            ;;
        G)
            USE_GIT=false
            ;;
        r)
            RERUN=${OPTARG}
            ;;
        t)
            TAG1D=${OPTARG}
            ;;
        k)
            SKIP2D=true
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

PREFIX=$1
if [ -z "$PREFIX" ] || [ -n "$2" ]; then
    usage
fi
BASEDIR="$(pwd)"

if [ "$SERVER" = "gfarm" ]; then
    # run 2D pipeline
    if [ "$SKIP2D" = false ]; then
        if $USE_GIT; then
            #pfs_integration_test.sh -r $RERUN -d $TARGET -c $CORES $PREFIX 2>&1 | tee test_e2e_pipe2d.log
            run_pipe2d_integration_test.sh -r $RERUN -d $TARGET -c $CORES -2 $PREFIX 2>&1 | tee test_e2e_pipe2d.log
        else
            cd $BASEDIR
            setup -jr drp_stella_data
            #pfs_integration_test.sh -r $RERUN -d $TARGET -c $CORES -G $PREFIX 2>&1 | tee test_e2e_pipe2d.log
            run_pipe2d_integration_test.sh -r $RERUN -d $TARGET -c $CORES -G -2 $PREFIX 2>&1 | tee test_e2e_pipe2d.log
        fi
    fi
    # find directories where pfsOBject files exist
    cd $BASEDIR
    mkdir -p $TAG1D
    mkdir -p $TAG1D/output
    cp -r calibration $TAG1D
    PFSOBJECT_DIR="$(pwd)"/$TARGET/rerun/$RERUN/pipeline/pfsObject/
    cd $PFSOBJECT_DIR
    find ./ -name "pfsObject*.fits" | awk '{gsub("/pfsObject"," ");print $1}' | uniq | while read dir; do   
        # run 1D pipeline
        echo $dir
        cd $PFSOBJECT_DIR
        drp_1dpipe --workdir=$BASEDIR/$TAG1D --spectra_dir=$PFSOBJECT_DIR/$dir --output_dir=$BASEDIR/$TAG1D/output --concurrency=$CORES --loglevel=INFO 2>&1 | tee $BASEDIR/test_e2e_pipe1d.log
    done
    cd $BASEDIR
elif [ "$SERVER" = "docker" ]; then
    # run 2D pipeline
    if [ "$SKIP2D" = false ]; then
        if $USE_GIT; then
            #pfs_integration_test.sh -r $RERUN -d $TARGET -c $CORES $PREFIX 2>&1 | tee test_e2e_pipe2d.log
            run_pipe2d_integration_test.sh -r $RERUN -d $TARGET -c $CORES -2 $PREFIX 2>&1 | tee test_e2e_pipe2d.log
        else
            cd $BASEDIR
            setup -jr drp_stella_data
            #pfs_integration_test.sh -r $RERUN -d $TARGET -c $CORES -G $PREFIX 2>&1 | tee test_e2e_pipe2d.log
            run_pipe2d_integration_test.sh -r $RERUN -d $TARGET -c $CORES -G -2 $PREFIX 2>&1 | tee test_e2e_pipe2d.log
        fi
    fi
    # find directories where pfsOBject files exist
    cd $BASEDIR
    mkdir -p $TAG1D
    mkdir -p $TAG1D/output
    cp -r calibration $TAG1D
    PFSOBJECT_DIR="$(pwd)"/$TARGET/rerun/$RERUN/pipeline/pfsObject/
    cd $PFSOBJECT_DIR
    find ./ -name "pfsObject*.fits" | awk '{gsub("/pfsObject"," ");print $1}' | uniq | while read dir; do   
        # run 1D pipeline
        echo $dir
        cd $PFSOBJECT_DIR
        drp_1dpipe --workdir=$BASEDIR/$TAG1D --spectra_dir=$PFSOBJECT_DIR/$dir --output_dir=$BASEDIR/$TAG1D/output --concurrency=$CORES --loglevel=INFO 2>&1 | tee $BASEDIR/test_e2e_pipe1d.log
    done
    cd $BASEDIR
else
    echo "Use gfarm or docker server"
fi

echo ""
echo "All done."
echo ""

