# This makes a container for the gear. Replace the first path next to the second COPY function 
# below with a path to your local compiled matlab function

FROM neurodebian:xenial
MAINTAINER Ozzy(ozenctaskin@hotmail.com)

#Copy everything into a container
ENV FLYWHEEL /flywheel/v0/
RUN mkdir -p ${FLYWHEEL}
COPY manifest.json run ${FLYWHEEL}
COPY code/* ${FLYWHEEL}
COPY standard_mesh_atlases.zip /standard_mesh_atlases.zip
RUN chmod +x /flywheel/v0/*

# Install required packages    
RUN apt-get update \
    && apt-get install -y \
    wget \
    python3 \
    python3-pip \
    zip \
    unzip \
    ants \
    connectome-workbench

# Install MCR on call
RUN pip3 install numpy nibabel==3.0.1

# Set the entrypoint  
ENTRYPOINT /flywheel/v0/run



