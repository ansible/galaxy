FROM centos:7

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off
ENV PIP_DEFAULT_TIMEOUT=60

ENV GALAXY_VENV /usr/share/galaxy/venv
ENV DJANGO_SETTINGS_MODULE galaxy.settings.development
ENV C_FORCE_ROOT 1

# Install node.js and yarn
RUN curl -sL -o '/tmp/nodesource-release-el7-1.noarch.rpm' \
        'https://rpm.nodesource.com/pub_8.x/el/7/x86_64/nodesource-release-el7-1.noarch.rpm' \
    && rpm -i --nosignature --force '/tmp/nodesource-release-el7-1.noarch.rpm' \
    && rm -f '/tmp/nodesource-release-el7-1.noarch.rpm' \
    && curl -sL -o '/etc/yum.repos.d/yarn.repo' 'https://dl.yarnpkg.com/rpm/yarn.repo' \
    && yum -y install nodejs yarn \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Install packages
RUN yum -y install epel-release \
    && yum -y install \
        gcc git make \
        python36 python36-devel \
        tmux ShellCheck vim \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Create directories structure
RUN mkdir -p /galaxy \
             /usr/share/galaxy \
             /var/lib/galaxy/media \
             /var/tmp/galaxy/imports \
             /var/tmp/galaxy/uploads \
             /var/run/galaxy

VOLUME ["/var/lib/galaxy", "/var/tmp/galaxy"]

# Install node dependencies
RUN yarn global add @angular/cli@6.1.2 \
    && ng set --global packageManager=yarn

# Create virtual environment and install python dependencies
COPY requirements/dev-requirements.txt /tmp/requirements.txt
RUN python3.6 -m venv "${GALAXY_VENV}" \
    && "${GALAXY_VENV}/bin/pip" install -U \
        'pip' \
        'wheel' \
        'setuptools' \
    && "${GALAXY_VENV}/bin/pip" install -r /tmp/requirements.txt

COPY scripts/docker/dev/entrypoint.sh /entrypoint

WORKDIR /galaxy
ENTRYPOINT ["/entrypoint"]
CMD ["start", "tmux"]
