FROM ros:humble

ARG USERNAME=USERNAME
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG WORKROOT=/home/void

# Delete user if it exists in container (e.g Ubuntu Noble: ubuntu)
RUN if id -u $USER_UID ; then userdel `id -un $USER_UID` ; fi

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Upgrade and get some misc stuff.
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y libboost-all-dev python3-pip wget

ENV SHELL=/bin/bash

# FP Needs realsense2.
RUN apt-get update && apt-get install -y \
    ros-$ROS_DISTRO-librealsense2 \
    ros-$ROS_DISTRO-realsense2-* \
    && rm -rf /var/lib/apt/lists/*

# Need libssl1.1.1 for Cuda (which got removed)
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb \
    && dpkg -i libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb

# Cuda 12.9
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb \
    && dpkg -i cuda-keyring_1.0-1_all.deb \
    && apt-get update && apt-get upgrade -y \
    && sudo apt-get -y install cuda-12-9 \
    && rm -rf /var/lib/apt/lists/*
#ENV PATH=/usr/local/cuda-12.9/bin${PATH:+:${PATH}}
ENV PATH=/usr/local/cuda-12.9/bin:${PATH}

USER $USERNAME

# Azure PAT workaround because git lfs over ssh is broken on Azure.
RUN --mount=type=secret,id=PAT \
    TOKEN=$(sudo cat /run/secrets/PAT) && \
    B64_TOKEN=$(printf "%s"":$TOKEN" | base64) && \
    git config --global --add http.extraHeader "Authorization: Basic ${B64_TOKEN}"

# Start doing things in the workspace...

# miniconda, -b batch mode, -u update existing
WORKDIR $WORKROOT
RUN mkdir -p miniconda3 \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3/miniconda.sh \
    && bash miniconda3/miniconda.sh -b -u -p miniconda3 \
    && rm miniconda3/miniconda.sh

# Clone FoundationPoseROS2
WORKDIR $WORKROOT
RUN git clone -b void_tmp https://voidvr@dev.azure.com/voidvr/TheVoid/_git/vdt_foundationpose_ros

# Finish miniconda setup since we are activating and create the fp_ros env.
WORKDIR $WORKROOT/vdt_foundationpose_ros
RUN . $WORKROOT/miniconda3/bin/activate \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
    && conda create -n foundationpose_ros python=3.10 -y

# And activate and build all of fp/fpros2.
RUN . $WORKROOT/miniconda3/bin/activate \
    && conda activate foundationpose_ros \
    && conda update -y -c conda-forge libstdcxx-ng \
    && conda install -y ruamel.yaml \ 
    && export PATH=/usr/local/cuda-12.9/bin${PATH:+:${PATH}}~ \
    && bash ./build_all_conda.sh
    #&& TORCH_CUDA_ARCH_LIST=8.9 bash ./build_all_conda.sh
    #&& bash ./build_all_conda.sh

# [Optional] Set the default user. Omit if you want to keep the default as root.
CMD ["/bin/bash"]
