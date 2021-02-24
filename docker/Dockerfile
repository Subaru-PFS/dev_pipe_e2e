# set the base image
FROM debian:10

# author
MAINTAINER Kiyoto Yabe

# extra metadata
LABEL version="1.0"
LABEL description="First image with Dockerfile."

# set up arguments
ARG INSTALL_DIR=/opt/pfs

# update sources list
RUN apt-get clean
RUN apt-get update

RUN apt-get install -qy wget curl patch locales rsync git git-lfs vim emacs gcc-7 g++-7
RUN apt-get install -qy build-essential libboost-all-dev  python3 python3-pip

# cleanup
USER root
RUN apt-get -qy autoremove

# add scripts to the container
ADD .bashrc /root/.bashrc
ADD .profile /root/.profile

# locales to UTF-8
RUN locale-gen C.UTF-8 && /usr/sbin/update-locale LANG=C.UTF-8
ENV LC_ALL C.UTF-8

# set environment
SHELL ["/bin/bash", "-c"]
ENV PYTHONIOENCODING UTF-8

# install PFS 2D pipelines

# install LSST prerequisites
RUN apt-get update --fix-missing
RUN apt-get install -qy bison ca-certificates cmake \
                        default-jre flex gettext libbz2-dev \
                        libcurl4-openssl-dev libfontconfig1 \
                        libglib2.0-dev libncurses5-dev libreadline6-dev \
                        libx11-dev libxrender1 libxt-dev m4 make \
                        perl-modules zlib1g-dev


# install PIPE2D

RUN useradd -m pfs
RUN mkdir -p ${INSTALL_DIR} && chown pfs:pfs ${INSTALL_DIR}

USER pfs
RUN mkdir -p ${INSTALL_DIR}/bin
RUN mkdir -p /home/pfs/bin
WORKDIR ${INSTALL_DIR}/bin
COPY ./install_lsst.sh /home/pfs/bin
COPY ./install_pfs.sh /home/pfs/bin
COPY ./build_pfs.sh /home/pfs/bin
WORKDIR ${INSTALL_DIR}

ENV CC gcc-7
ENV CXX g++-7

RUN /home/pfs/bin/install_pfs.sh -t current ${INSTALL_DIR}/stack 2>&1 | tee install_pfs.log

# install SIM2D

USER pfs
WORKDIR $INSTALL_DIR
RUN . /opt/pfs/stack/loadLSST.bash \
 && setup sconsUtils \
 && pip install fitsio \
 && for pkg in drp_instdata drp_instmodel ; do \
      git clone -b master git://github.com/Subaru-PFS/$pkg || git clone git://github.com/Subaru-PFS/$pkg ; \
      cd $pkg \
      && setup -k -r . \
      && eups declare $pkg latest -t current -r . \
      && cd ..; \
    done \
 && mkdir -p /home/pfs/.config/matplotlib \
 && echo "backend : TkAgg" > /home/pfs/.config/matplotlib/matplotlibrc

# install PFS 1D pipelines

# install Amazed prerequisites
USER root
RUN apt-get install -qy swig pkg-config libboost-all-dev libgsl-dev \
                        libcfitsio-dev libfftw3-dev

# install drp_1d + drp_1dpipe
USER pfs
RUN mkdir -p /home/pfs/pipe1d

RUN . /opt/pfs/stack/loadLSST.bash \
 && cd /home/pfs/pipe1d \
 && git clone https://github.com/Subaru-PFS/drp_1d.git \
 && cd drp_1d \
 && mkdir build; cd build \
 &&  cmake .. -DCMAKE_INSTALL_PREFIX=/opt/pfs/pipe1d \
 && make -j 4 \
 && make install \
 && cd .. \
 && pip install . \
 && cd build \
 && make test

RUN . /opt/pfs/stack/loadLSST.bash \
 && setup pfs_pipe2d -t current \
 && pip install numpy==1.16.5 \
 && cd /home/pfs/pipe1d \
 && git clone https://github.com/Subaru-PFS/drp_1dpipe \
 && cd drp_1dpipe \
 && pip install .
# && pytest

# install pipe_e2e
USER pfs
RUN mkdir -p /home/pfs/pipe_e2e
WORKDIR /home/pfs/pipe_e2e

RUN . /opt/pfs/stack/loadLSST.bash \
 && setup pfs_pipe2d -t current \
 && git clone https://github.com/Subaru-PFS/dev_pipe_e2e.git \
 && cd dev_pipe_e2e \
 && eups declare pfs_pipe_e2e git -t current -r . \
 && cd ..


# prepare regular processing test 
ARG PROCESSING_DIR=/home/pfs/pipe_e2e/regular_processing

USER pfs
WORKDIR $INSTALL_DIR
RUN git clone https://github.com/Subaru-PFS/pfs_pipe2d.git

RUN mkdir -p ${PROCESSING_DIR}
ADD regular_processing/*.sh ${PROCESSING_DIR}/
ADD regular_processing/parameters_e2e.json ${PROCESSING_DIR}/
ADD regular_processing/drp_stella_data/ ${PROCESSING_DIR}/drp_stella_data/
ADD regular_processing/examples/ ${PROCESSING_DIR}/examples/
WORKDIR ${PROCESSING_DIR}

# finish
USER pfs
WORKDIR /home/pfs
CMD /bin/bash
