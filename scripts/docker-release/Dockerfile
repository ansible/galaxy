FROM centos:7

RUN useradd -r -m -g root galaxy

ENV PIP_NO_CACHE_DIR off

# Install python
RUN yum -y install epel-release \
    && yum -y install python python-pip \
    && pip install virtualenv \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Install tini
ENV TINI_VERSION v0.16.1
RUN yum -y install wget \
    && wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini" \
    && chmod +x /usr/local/bin/tini \
    && yum -y remove wget \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Create directories structure
RUN mkdir -p /etc/galaxy \
    && mkdir -p /var/log/galaxy \
    && mkdir -p /var/lib/galaxy/public \
    && chown galaxy:root /var/log/galaxy \
    && chmod g+w /var/log/galaxy

# Install python dependencies
ENV VENV_BIN /var/lib/galaxy/venv/bin
COPY requirements.txt /tmp/requirements.txt
RUN virtualenv /var/lib/galaxy/venv \
    && ${VENV_BIN}/pip install -U pip \
    && ${VENV_BIN}/pip install -r /tmp/requirements.txt

COPY scripts/docker-release/entrypoint.sh /entrypoint.sh
COPY dist/ /tmp/dist
COPY build/static /var/lib/galaxy/public/static

RUN ${VENV_BIN}/pip install $(readlink -f /tmp/dist/galaxy.whl) \
    && rm -rf /tmp/dist

# Copy test data
RUN mkdir -p /galaxy/test-data
COPY test-data/* /galaxy/test-data/

WORKDIR /galaxy

ENV DJANGO_SETTINGS_MODULE galaxy.settings.production

USER galaxy
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run", "web"]
