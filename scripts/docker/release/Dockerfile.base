# vim: set ft=Dockerfile:
FROM centos:7

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PIP_NO_CACHE_DIR off
ENV GALAXY_VENV /usr/share/galaxy/venv

# Install packages and create virtual environment
RUN yum -y install epel-release \
    && yum -y install git gcc make python36 python36-devel \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Install python dependencies
COPY requirements/requirements.txt /tmp/requirements.txt
RUN python3.6 -m venv ${GALAXY_VENV} \
    && "${GALAXY_VENV}/bin/pip" install -U \
        'pip' \
        'wheel' \
        'setuptools' \
    && "${GALAXY_VENV}/bin/pip" install -r /tmp/requirements.txt
