FROM ubuntu:22.04

RUN useradd --create-home --shell /bin/bash user
WORKDIR /home/user

ADD main.py .

# Install PDAL
RUN apt-get update && apt-get install -y pdal

# Install Anaconda
RUN apt-get update && apt-get install -y wget bzip2
RUN wget --quiet https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh -O ~/anaconda.sh
RUN /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh && \
    echo 'export PATH="/opt/conda/bin:$PATH"' >> ~/.bashrc

# Configure the environment
ENV PATH /opt/conda/bin:$PATH
RUN conda create -n optimenv python=3.6.13
RUN echo "conda activate optimenv" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH
# RUN conda install -c conda-forge pdal python-pdal
# RUN conda install -c conda-forge entwine
COPY requirements.txt .
USER root

# Output folder structure
RUN mkdir -p /home/user/output/footprint_tiles
RUN chown user /home/user/output/footprint_tiles
RUN mkdir -p /home/user/output/indexed_pointcloud
RUN chown user /home/user/output/indexed_pointcloud
RUN mkdir -p /home/user/output/pointcloud_tiles
RUN chown user /home/user/output/pointcloud_tiles
RUN mkdir -p /home/user/output/model
RUN chown user /home/user/output/model
RUN mkdir -p /home/user/output/model/cityjson
RUN chown user /home/user/output/model/cityjson
RUN mkdir -p /home/user/output/model/obj
RUN chown user /home/user/output/model/obj

# Update package manager and install necessary tools
RUN apt-get update && \
    apt-get install -y wget build-essential

# Set the OPENSSL_ROOT_DIR environment variable
ENV OPENSSL_ROOT_DIR=/usr/local/openssl

# Download and install OpenSSL
RUN wget https://www.openssl.org/source/openssl-1.1.1k.tar.gz && \
    tar -xzvf openssl-1.1.1k.tar.gz && \
    cd openssl-1.1.1k && \
    ./config --prefix=$OPENSSL_ROOT_DIR && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    rm -rf openssl-1.1.1k openssl-1.1.1k.tar.gz

# Set the OpenSSL library and header paths
ENV OPENSSL_CRYPTO_LIBRARY=$OPENSSL_ROOT_DIR/lib/libcrypto.a
ENV OPENSSL_INCLUDE_DIR=$OPENSSL_ROOT_DIR/include

# Install Git and CMake
RUN apt-get update && \
    apt-get install -y git
RUN wget https://cmake.org/files/v3.21/cmake-3.21.0.tar.gz
RUN tar -xzvf cmake-3.21.0.tar.gz
WORKDIR cmake-3.21.0
RUN ./configure --prefix=/usr/local --no-system-libs
RUN make -j$(nproc) && \
    make install
RUN rm -rf cmake-3.21.0.tar.gz cmake-3.21.0
WORKDIR /home/user

# Install Nlohmann JSON 1.5.0
RUN apt-get update && \
    git clone https://github.com/nlohmann/json.git && \
    cd json && mkdir build && cd build && cmake .. && make && make install && \
    cd ../.. && rm -rf json

# Install CURL
RUN apt-get update && \
    apt-get install -y curl libssl-dev libcurl4-openssl-dev

ENV CURL_INCLUDE_DIR=/usr/include/curl
ENV CURL_LIBRARY=/usr/lib/x86_64-linux-gnu/libcurl.so

# Install PROJ
RUN apt-get update && \
    apt-get install -y libproj-dev libtiff-dev

ENV TIFF_INCLUDE_DIR=/usr/include/x86_64-linux-gnu/
ENV TIFF_LIBRARY=/usr/lib/x86_64-linux-gnu/libtiff.so

RUN git clone https://github.com/OSGeo/PROJ.git \
    && cd PROJ \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install

ENV LD_LIBRARY_PATH=/usr/local/lib

# Install glfw3, pkg-config and gtk
RUN apt-get update && \
    apt-get install -y \
    libglfw3 \
    libglfw3-dev \
    pkg-config \
    libgtk2.0-0 \
    libgtk2.0-dev

# Install lasLib
RUN apt-get update && \
    apt-get install -y \
    libboost-all-dev \
    libgeotiff-dev \
    libtiff5-dev \
    libz-dev

RUN apt-get update && apt-get install -y unzip
RUN apt-get update && apt-get install -y libjpeg62 libpng16-16 libc6

RUN git clone https://github.com/LAStools/LAStools.git \
    && cd LAStools \
    && cmake . \
    && make \
    && make install

# Install Eigen3
RUN apt-get update && apt-get install -y libeigen3-dev

# Install CGAL
RUN apt-get update && apt-get install -y libgmp-dev libcgal-dev
RUN wget https://github.com/CGAL/cgal/releases/download/v5.4.3/CGAL-5.4.3.tar.xz \
    && tar -xvf CGAL-5.4.3.tar.xz \
    && cd CGAL-5.4.3 \
    && cmake . \
    && make \
    && make install \
    && cd .. && rm -rf CGAL-5.4.3 CGAL-5.4.3.tar.xz

# Install GEOS and GDAL
RUN apt-get update && \
    apt-get install -y libgeos-dev gdal-bin libgdal-dev

ENV GEOS_CONFIG=/usr/bin/geos-config
ENV GDAL_CONFIG=/usr/bin/gdal-config

# Install Val3dity
RUN git clone https://github.com/tudelft3d/val3dity.git \
    && cd LAStools \
    && cmake . \
    && make \
    && make install

# Install GeoFlow-bundle
COPY geoflow-bundle /home/user/geoflow-bundle
RUN cd geoflow-bundle && mkdir build && cd build && cmake .. && \
    cmake --build . --config Release --parallel 4 && \
    cmake --install .
WORKDIR /home/user

# Install Mambaforge
RUN curl -sL https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh -o /tmp/mambaforge.sh && \
    /bin/bash /tmp/mambaforge.sh -b -p /opt/mambaforge && \
    rm /tmp/mambaforge.sh

ENV PATH=/opt/mambaforge/bin:$PATH

# Installing Entwine, PDAL, python-PDAL and Optim3D
RUN mamba install -y mamba && \
    mamba update -y --all && \
    mamba install -y entwine pdal python-pdal

RUN pip install optim3d==0.2.9

CMD ["python", "-c", "while True: pass"]