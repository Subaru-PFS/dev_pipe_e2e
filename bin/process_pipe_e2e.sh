#!/bin/bash

# default configuration
SERVER="proc-spt"
REPO="pipe_e2e_test"  # Directory name to give data repo
DATADIR="weekly-20210819"
TARGET1D="pipe1d_workdir" # Directory name for 1D results
CORES=8       # Number of cores to use
USE_GIT=true  # checkout/update from git
SKIP2D=false
WEEKLY=false

usage() {
    # Display usage and quit
    echo "Run the PFS pipeline end-to-end process." 1>&2
    echo "" 1>&2
    echo "Usage: $0 [-s <SERVER>] [-r <RERUN>] [-d <DATADIR>] [-t <TARGET1D>] [-c <CORES>] [-G] [-k] [-w] WORKDIR" 1>&2
    echo "" 1>&2
    echo "    -s <SERVER> : server name to use (default: ${SERVER})" 1>&2
    echo "    -r <REPO> : rerun name to use (default: ${REPO})" 1>&2
    echo "    -d <DATADIR> : path to raw data (default: ${DATADIR})" 1>&2
    echo "    -t <TARGET1D> : directory name to put 1D results (default: ${TAG1D})" 1>&2
    echo "    -c <CORES> : number of cores to use (default: ${CORES})" 1>&2
    echo "    -G : don't clone or update from git" 1>&2
    echo "    -k : skip 2D procedure" 1>&2
    echo "    -w : weekly sample (not science sample)" 1>&2
    echo "    WORKDIR : directory under which to operate" 1>&2
    echo "" 1>&2
    #exit 1
}

# Parse command-line arguments
while getopts ":s:r:d:t:Gkwc:" opt; do
    case "${opt}" in
        s)
            SERVER=${OPTARG}
            ;;
        r)
            REPO=${OPTARG}
            ;;
        d)
            DATADIR=${OPTARG}
            ;;
        t)
            TARGET1D=${OPTARG}
            ;;
        G)
            USE_GIT=false
            ;;
        k)
            SKIP2D=true
            ;;
        w)
            WEEKLY=true
            ;;
        c)
            CORES=${OPTARG}
            ;;
        h | *)
            usage
            ;;
    esac
done

shift $((OPTIND-1))
WORKDIR=$1; shift
if [ -z "$WORKDIR" ] || [ -n "$1" ]; then
    usage
fi

BASEDIR="$(pwd)"

if [ "$SERVER" = "proc-spt" ]; then
    SRC="/simdata/proc-spt/drp/pipe_e2e/regular_processing_new/src/"
    # run 2D pipeline
    if [ "$SKIP2D" = false ]; then
        if [ "$USE_GIT" = true ]; then
            cd $BASEDIR
            if [ "$WEEKLY" = true ]; then
                ''' run weekly '''
                echo "run 2D pipeline (weekly)" | tee test_e2e_pipe2d_weekly.log
                $SRC/pfs_pipe2d/weekly/process_weekly.sh -d $DATADIR -r weekly -c $CORES -n -D $REPO 2>&1 | tee -a test_e2e_pipe2d_weekly.log
            else
                ''' run science '''
                echo "run 2D pipeline (science)" | tee test_e2e_pipe2d_science.log
                $SRC/pfs_pipe2d/weekly/process_science.sh -d $DATADIR -r science -c $CORES -D $REPO 2>&1 | tee -a test_e2e_pipe2d_science.log
            fi
        else
            cd $BASEDIR
            if [ "$WEEKLY" = true ]; then
                ''' run weekly '''
                echo "run 2D pipeline (weekly)" | tee test_e2e_pipe2d_weekly.log
                $SRC/pfs_pipe2d/weekly/process_weekly.sh -d $DATADIR -r weekly -c $CORES -n -D $REPO 2>&1 | tee -a test_e2e_pipe2d_weekly.log
            else
                ''' run science '''
                echo "run 2D pipeline (science)" | tee test_e2e_pipe2d_science.log
                $SRC/pfs_pipe2d/weekly/process_science.sh -d $DATADIR -r science -c $CORES -D $REPO 2>&1 | tee -a test_e2e_pipe2d_science.log
            fi
        fi
    fi
    # find directories where pfsOBject files exist
    cd $BASEDIR
    mkdir -p $TARGET1D
    mkdir -p $TARGET1D/output
    cp -r calibration $TARGET1D
    if [ "$WEEKLY" = true ]; then
        # weekly sample #
        echo "run 1D pipeline (weekly)" 2>&1 | tee test_e2e_pipe1d_weekly.log
        # brn dataset
        PFSOBJECT_DIR=$REPO/rerun/weekly/pipeline/brn/pipeline/pfsObject/
        cd $PFSOBJECT_DIR
        find ./ -name "pfsObject*.fits" | awk '{gsub("/pfsObject"," ");print $1}' | uniq | while read dir; do   
            # run 1D pipeline
            echo $dir 2>&1 | tee -a $BASEDIR/test_e2e_pipe1d_weekly.log
            cd $PFSOBJECT_DIR
            drp_1dpipe --workdir=$TARGET1D --spectra_dir=$PFSOBJECT_DIR/$dir --output_dir=$TARGET1D/output --concurrency=$CORES --loglevel=INFO 2>&1 | tee -a $BASEDIR/test_e2e_pipe1d_weekly.log
        done
        # bmn dataset
        PFSOBJECT_DIR=$REPO/rerun/weekly/pipeline/bmn/pipeline/pfsObject/
        cd $PFSOBJECT_DIR
        find ./ -name "pfsObject*.fits" | awk '{gsub("/pfsObject"," ");print $1}' | uniq | while read dir; do   
            # run 1D pipeline
            echo $dir 2>&1 | tee -a $BASEDIR/test_e2e_pipe1d_weekly.log
            cd $PFSOBJECT_DIR
            drp_1dpipe --workdir=$TARGET1D --spectra_dir=$PFSOBJECT_DIR/$dir --output_dir=$TARGET1D/output --concurrency=$CORES --loglevel=INFO 2>&1 | tee -a $BASEDIR/test_e2e_pipe1d_weekly.log
        done
    else
        # science sample #
        echo "run 1D pipeline (science)" 2>&1 | tee test_e2e_pipe1d_science.log
        PFSOBJECT_DIR=$REPO/rerun/science/pipeline/pfsObject/
        cd $PFSOBJECT_DIR
        find ./ -name "pfsObject*.fits" | awk '{gsub("/pfsObject"," ");print $1}' | uniq | while read dir; do   
            # run 1D pipeline
            echo $dir 2>&1 | tee -a $BASEDIR/test_e2e_pipe1d_science.log
            cd $PFSOBJECT_DIR
            drp_1dpipe --workdir=$TARGET1D --spectra_dir=$PFSOBJECT_DIR/$dir --output_dir=$TARGET1D/output --concurrency=$CORES --loglevel=INFO 2>&1 | tee -a $BASEDIR/test_e2e_pipe1d_science.log
        done
    fi
    cd $BASEDIR
elif [ "$SERVER" = "gfarm" ]; then
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
    echo "Use proc-spt(docker) or gfarm server"
fi

echo ""
echo "All done."
echo ""
