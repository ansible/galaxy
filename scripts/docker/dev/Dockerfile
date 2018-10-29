FROM fedora:27

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR off

# FIXME(cutwater): Run galaxy and celery under unprivileged user
ENV C_FORCE_ROOT 1
ENV DJANGO_SETTINGS_MODULE galaxy.settings.development


# Install nodejs and yarn
RUN curl -sL -o '/tmp/nodesource-release-fc27-1.noarch.rpm' \
        'https://rpm.nodesource.com/pub_8.x/fc/27/x86_64/nodesource-release-fc27-1.noarch.rpm' \
    && rpm -i --nosignature --force '/tmp/nodesource-release-fc27-1.noarch.rpm' \
    && rm -f '/tmp/nodesource-release-fc27-1.noarch.rpm' \
    && curl -sL -o '/etc/yum.repos.d/yarn.repo' 'https://dl.yarnpkg.com/rpm/yarn.repo' \
    && dnf -y install nodejs yarn \
    && dnf -y clean all \
    && rm -rf /var/cache/yum


# Install packages and create virtual environment
RUN dnf -y install \
        findutils gcc git make \
        vim tmux ShellCheck \
        python3 python3-pip python3-devel \
    && dnf -y clean all \
    && rm -rf /var/cache/yum


# Install node dependencies
# FIXME(cutwater): Drop global angular/cli installation
RUN yarn global add @angular/cli@6.1.2 \
    && ng set --global packageManager=yarn


# Install python dependencies
COPY requirements.txt /tmp/requirements.txt
ENV VENV_BIN /var/lib/galaxy/venv/bin
RUN mkdir -p /var/lib/galaxy/ \
    && python3 -m venv /var/lib/galaxy/venv \
    && ${VENV_BIN}/pip install -U pip wheel \
    # TODO(cutwater): Move to dev-requirements.txt
    && ${VENV_BIN}/pip install honcho flake8 \
    && ${VENV_BIN}/pip install -r /tmp/requirements.txt


# Install galaxy lint rules
# FIXME(cutwater): Better location \ install as python package
RUN git clone --depth 1 \
        https://github.com/ansible/galaxy-lint-rules.git \
        /usr/local/galaxy-lint-rules


COPY scripts/docker/dev/entrypoint.sh /entrypoint.sh
WORKDIR /galaxy
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/galaxy/scripts/docker/dev/start-develop.sh"]
