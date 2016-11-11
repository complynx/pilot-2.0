FROM hepsw/cvmfs-atlas

RUN mv $HOME/.bashrc $HOME/.bashrc1
ADD tools/new_bashrc.sh $HOME/.bashrc2
RUN cat $HOME/.bashrc1 $HOME/.bashrc2 > $HOME/.bashrc && rm -rf $HOME/.bashrc1 $HOME/.bashrc2
ADD . /repo
WORKDIR /repo
RUN wget https://bootstrap.pypa.io/ez_setup.py
RUN wget https://bootstrap.pypa.io/get-pip.py
