# This makes a container for the gear. Replace the first path next to the second COPY function 
# below with a path to your local compiled matlab function

FROM neurodebian:xenial
MAINTAINER Ozzy(ozenctaskin@hotmail.com)

#Copy everything into a container
ENV FLYWHEEL /flywheel/v0/
RUN mkdir -p ${FLYWHEEL}
COPY manifest.json run ${FLYWHEEL}
COPY locate_file.py map_fs2gifti.py map_vol2fs.py ${FLYWHEEL}
COPY standard_mesh_atlases.zip /standard_mesh_atlases.zip
COPY fslinstaller.py /fslinstaller.py
RUN chmod +x /flywheel/v0/*

# Install required packages     
RUN apt-get update \
    && apt-get install -y \
    software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y \
    wget \
    zip \
    unzip \
    ants \
    connectome-workbench

# Install Anaconda
RUN wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
RUN bash Anaconda3-2020.02-Linux-x86_64.sh -b -p /anaconda3
ENV PATH=$PATH:/anaconda3/bin

# Install python2 for fslinstallation and install the newest verison of fsl
RUN apt-get install python -y
RUN python2 /fslinstaller.py -d /fsl 

# Install the required python packages
RUN pip install 'numpy==1.18.1' 'nibabel==3.1.0' 'neuropythy==0.11.5' 'nilearn==0.6.2' 'scikit-learn==0.22.1' 'matplotlib==3.1.3' 'pandas==1.0.3' 'scipy==1.4.1' 'hcp-utils==0.1.0' 'ciftify'

# Download and install Freesurfer on call
RUN wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz
RUN mkdir freesurfer
RUN tar -zxf freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz 
COPY license.txt /freesurfer/license.txt
ENV FREESURFER_HOME /freesurfer

# Set the entrypoint  
ENTRYPOINT /flywheel/v0/run



