FROM ros:humble-perception 

ARG USERNAME=USERNAME
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG WORKROOT=/home/void

# Delete user if it exists in container (e.g Ubuntu Noble: ubuntu)
RUN if id -u $USER_UID ; then userdel `id -un $USER_UID` ; fi

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # /dev/video access
    && usermod -a -G video $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Upgrade and get some misc stuff.
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y ca-certificates curl libboost-all-dev python3-pip unzip wget

ENV SHELL=/bin/bash

# realsense2 and other deps.
RUN apt-get update && apt-get install -y \
    ros-$ROS_DISTRO-apriltag-ros \
    ros-$ROS_DISTRO-librealsense2 \
    ros-$ROS_DISTRO-realsense2-* \
    ros-${ROS_DISTRO}-web-video-server \
    && rm -rf /var/lib/apt/lists/*

# Need libssl1.1.1 for Cuda (which got removed)
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb \
    && dpkg -i libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb

# cuda 12.1 (not 12.9) requires keyboard-configuration which tries to ask.
ENV DEBIAN_FRONTEND=noninteractive

# Cuda 12.1
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb \
    && dpkg -i cuda-keyring_1.0-1_all.deb \
    && apt-get update && apt-get upgrade -y \
    && apt-get -y install cuda-12-6 \
    && rm -rf /var/lib/apt/lists/*
#ENV PATH=/usr/local/cuda-12.9/bin${PATH:+:${PATH}}
ENV PATH=/usr/local/cuda-12.6/bin:${PATH}

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,graphics,utility

USER $USERNAME

# Azure PAT workaround because git lfs over ssh is broken on Azure.
RUN --mount=type=secret,id=PAT \
    TOKEN=$(sudo cat /run/secrets/PAT) && \
    B64_TOKEN=$(printf "%s"":$TOKEN" | base64) && \
    git config --global --add http.extraHeader "Authorization: Basic ${B64_TOKEN}"

    
# Start doing things in the workspace...

# rosdep init called by base for root but not $USERNAME.
RUN rosdep fix-permissions && \
    rosdep update --rosdistro $ROS_DISTRO

#
# miniconda
#

# miniconda, -b batch mode, -u update existing
WORKDIR $WORKROOT
RUN mkdir -p miniconda3 \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda3/miniconda.sh \
    && bash miniconda3/miniconda.sh -b -u -p miniconda3 \
    && rm miniconda3/miniconda.sh \
    && . $WORKROOT/miniconda3/bin/activate \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

#
# uv
#

# Download the latest installer
ADD --chmod=700 --chown=void:void https://astral.sh/uv/install.sh "/home/$USERNAME/uv-installer.sh"
# Run the installer then remove it
RUN sh "/home/$USERNAME/uv-installer.sh" && rm "/home/$USERNAME/uv-installer.sh"
# Ensure the installed binary is on the `PATH`
ENV PATH="/home/$USERNAME/.local/bin/:$PATH"

#
# FoundationPoseROS2
#

# WORKDIR $WORKROOT
# RUN git clone -b void_tmp https://voidvr@dev.azure.com/voidvr/TheVoid/_git/vdt_foundationpose_ros

# # Finish miniconda setup since we are activating and create the fp_ros env.
# WORKDIR $WORKROOT/vdt_foundationpose_ros
# RUN . $WORKROOT/miniconda3/bin/activate \
#     && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
#     && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
#     && conda create -n foundationpose_ros python=3.10 -y

# # And activate and build all of fp/fpros2.
# RUN . $WORKROOT/miniconda3/bin/activate \
#     && conda activate foundationpose_ros \
#     && conda update -y -c conda-forge libstdcxx-ng \
#     && conda install -y ruamel.yaml \ 
#     && export PATH=/usr/local/cuda-12.9/bin${PATH:+:${PATH}}~ \
#     #&& bash ./build_all_conda.sh
#     && TORCH_CUDA_ARCH_LIST=8.9 bash ./build_all_conda.sh


#
# happypose
#

# happypose (has submodules) NOTE the branch: dev.
WORKDIR $WORKROOT
RUN git clone --branch dev --recursive https://github.com/agimus-project/happypose.git $WORKROOT/happypose
#RUN git clone --branch dev https://voidvr@dev.azure.com/voidvr/TheVoid/_git/vdt_happypose $WORKROOT/happypose

WORKDIR $WORKROOT/happypose

# 1. uv
# RUN uv venv —-seed --system-site-packages && \ 
#     uv sync --extra pypi --extra cu124

# OR

# 2. conda
# RUN . $WORKROOT/miniconda3/bin/activate \
#     && conda create --name happypose python=3.10 \
#     && conda env update --file environment.yml \
#     && conda activate happypose \
#     && pip install -r requirements/base.txt \
#     #&& pip install -r requirements/cu124.txt \
#     && pip install catkin_pkg empy==3.3.4 lark

RUN . $WORKROOT/miniconda3/bin/activate \
    && conda create --name happypose python=3.10 \
    #&& sed -i 's/    - torchnet/#    - torchnet/' environment.yml \
    && sed -i '7d;9d;10d;15d;17d' environment.yml \
    && conda env update --file environment.yml

RUN . $WORKROOT/miniconda3/bin/activate \
    && conda activate happypose \
    #conda install libtiff==4.5.1 -c conda-forge XXX
    # 49: torchnet 113: torchnet
    && sed -i '49d;113d' pyproject.toml \
    # 353: torchnet 403: visdom
    && sed -i '353d;355d;403d' requirements/base.txt \
    #&& sed -i '407d;462d' requirements/cu124.txt \
    && pip install -r requirements/base.txt \
    && pip3 install --upgrade torch torchvision --index-url https://download.pytorch.org/whl/cu126 \
    && pip install catkin_pkg empy==3.3.4 lark ultralytics

# OR

# 3. plain host pip DOES NOT WORK because the reqs files are generated by uv and require uv
#RUN pip install -r requirements/pypi.txt -r requirements/cu124.txt

#
# happypose_data
#

#RUN mkdir -p $WORKROOT/happypose_data
COPY --chown=void:void happypose_data $WORKROOT/happypose_data
ENV HAPPYPOSE_DATA_DIR="$WORKROOT/happypose_data"

#
# happypose_ros
#

# happypose_ros (no submodules)
WORKDIR $WORKROOT
RUN git clone https://github.com/agimus-project/happypose_ros $WORKROOT/happypose_ros/
#RUN git clone https://voidvr@dev.azure.com/voidvr/TheVoid/_git/vdt_happypose_ros $WORKROOT/happypose_ros/

WORKDIR $WORKROOT/happypose_ros

RUN . $WORKROOT/miniconda3/bin/activate && \
    conda activate happypose && \
#RUN . $WORKROOT/happypose/.venv/bin/activate && \
    . /opt/ros/$ROS_DISTRO/setup.sh && \
    sudo apt-get update && \
    rosdep install -y --from-paths . --ignore-src --rosdistro $ROS_DISTRO && \
    sudo rm -rf /var/lib/apt/lists/*

RUN . $WORKROOT/miniconda3/bin/activate && \
    conda activate happypose && \
# RUN . $WORKROOT/happypose/.venv/bin/activate && \
    . /opt/ros/$ROS_DISTRO/setup.sh && \
    colcon build --symlink-install


CMD ["/bin/bash"]
