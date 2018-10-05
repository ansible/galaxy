FROM galaxy-base:latest

# Install tini
ENV TINI_VERSION v0.16.1
RUN yum -y install wget \
    && wget -O /usr/local/bin/tini \
        "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini" \
    && chmod +x /usr/local/bin/tini \
    && yum -y remove wget \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Create galaxy user
ENV HOME /var/lib/galaxy
RUN mkdir -p /var/lib/galaxy \
    && useradd --system --gid root \
        --home-dir "${HOME}" galaxy

# Create directories structure
RUN mkdir -p /etc/galaxy \
             /var/log/galaxy \
             /var/lib/galaxy/public \
             /var/lib/galaxy/downloads

COPY scripts/docker/release/entrypoint.sh /entrypoint.sh
COPY --from=galaxy-build:latest /galaxy/dist/VERSION /var/lib/galaxy
COPY --from=galaxy-build:latest /galaxy/dist/*.whl /tmp
COPY --from=galaxy-build:latest /galaxy/build/static/ /var/lib/galaxy/public/static/
RUN ${VENV_BIN}/pip install "/tmp/galaxy-$(< /var/lib/galaxy/VERSION)-py2-none-any.whl"

RUN git clone https://github.com/ansible/galaxy-lint-rules.git /usr/local/galaxy-lint-rules

# Fix directory permissions
RUN chown -R galaxy:root \
        /etc/galaxy \
        /var/log/galaxy \
        /var/lib/galaxy \
    && chmod -R u=rwX,g=rwX\
        /etc/galaxy \
        /var/log/galaxy \
        /var/lib/galaxy

WORKDIR /var/lib/galaxy

ENV DJANGO_SETTINGS_MODULE galaxy.settings.production
# Workaround for git running under different users
# See https://github.com/jenkinsci/docker/issues/519
ENV GIT_COMMITTER_NAME 'Ansible Galaxy'
ENV GIT_COMMITTER_EMAIL 'galaxy@ansible.com'

USER galaxy
EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["run", "web"]
