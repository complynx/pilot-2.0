FROM hepsw/cvmfs-atlas
ARG REPO_DIR=.

ENV TOXENV py27

RUN mv .bashrc .bashrc_o
ADD new_bashrc.sh $HOME/.bashrc
ADD $REPO_DIR /repo