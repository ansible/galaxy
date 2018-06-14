FROM galaxy-base:latest

RUN useradd -r -m -g root galaxy

# Install tini
ENV TINI_VERSION v0.16.1
RUN yum -y install wget \
    && wget -O /usr/local/bin/tini \
        "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini" \
    && chmod +x /usr/local/bin/tini \
    && yum -y remove wget \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Create directories structure
RUN mkdir -p /etc/galaxy \
             /var/log/galaxy \
             /var/lib/galaxy/public \
    && chown galaxy:root /etc/galaxy \
                         /var/log/galaxy \
                         /var/lib/galaxy/public \
    && chmod g+w /etc/galaxy \
                 /var/log/galaxy \
                 /var/lib/galaxy/public

COPY scripts/docker/release/entrypoint.sh /entrypoint.sh
COPY --from=galaxy-build:latest /galaxy/dist/VERSION /var/lib/galaxy
COPY --from=galaxy-build:latest /galaxy/dist/*.whl /tmp
COPY --from=galaxy-build:latest /galaxy/build/static/ /var/lib/galaxy/public/static/
RUN ${VENV_BIN}/pip install "/tmp/galaxy-$(< /var/lib/galaxy/VERSION)-py2-none-any.whl"

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
