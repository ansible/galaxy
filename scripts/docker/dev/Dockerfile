FROM centos:7

# Install nodejs and yarn
# TODO(cutwater): Use direct package link instead of
# setup_8.x script execution.
RUN yum -y install wget \
    && wget -O - https://rpm.nodesource.com/setup_8.x | bash - \
    && wget -O /etc/yum.repos.d/yarn.repo https://dl.yarnpkg.com/rpm/yarn.repo \
    && yum -y install nodejs yarn \
    && yum -y remove wget \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Install packages and create virtual environment
ENV PIP_NO_CACHE_DIR off
RUN yum -y install epel-release \
    && yum -y install gcc git make python python-pip python-devel \
    && pip install virtualenv \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Install node dependencies
RUN yarn global add @angular/cli \
    && ng set --global packageManager=yarn

# Install python dependencies
COPY requirements.txt /tmp/requirements.txt
ENV VENV_BIN /var/lib/galaxy/venv/bin
RUN mkdir -p /var/lib/galaxy/ \
    && virtualenv /var/lib/galaxy/venv \
    && ${VENV_BIN}/pip install -U pip wheel \
    && ${VENV_BIN}/pip install -r /tmp/requirements.txt

RUN yum -y install vim tmux make
RUN ${VENV_BIN}/pip install honcho flake8
RUN localedef -c -i en_US -f UTF-8 en_US.UTF-8

ENV DJANGO_SETTINGS_MODULE galaxy.settings.development

ENV C_FORCE_ROOT 1

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf8

COPY scripts/docker/dev/entrypoint.sh /entrypoint.sh

WORKDIR /galaxy
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/galaxy/scripts/docker/dev/start-develop.sh"]
