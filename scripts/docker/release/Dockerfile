FROM galaxy-base:latest

# Install tini
ENV TINI_VERSION v0.18.0
RUN curl -sL -o '/usr/local/bin/tini' \
        "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini" \
    && chmod +x /usr/local/bin/tini \
    && yum -y clean all \
    && rm -rf /var/cache/yum

# Create galaxy user
ENV HOME /var/lib/galaxy
RUN mkdir -p /var/lib/galaxy \
    && useradd --system --gid root --home-dir "${HOME}" galaxy

# Create directories structure
RUN mkdir -p /etc/galaxy \
             /usr/share/galaxy/public \
             /var/lib/galaxy/media \
             /var/run/galaxy \
             /var/tmp/galaxy/imports \
             /var/tmp/galaxy/uploads

COPY scripts/docker/release/entrypoint.sh /entrypoint
COPY --from=galaxy-build:latest /galaxy/dist/VERSION /usr/share/galaxy/
COPY --from=galaxy-build:latest /galaxy/dist/*.whl /tmp
COPY --from=galaxy-build:latest /galaxy/build/static /usr/share/galaxy/public/
RUN _galaxy_wheel="/tmp/galaxy-$(< /usr/share/galaxy/VERSION)-py3-none-any.whl" \
    && "${GALAXY_VENV}/bin/pip" install "${_galaxy_wheel}" \
    && rm -f "${_galaxy_wheel}"


# Fix directory permissions
RUN chown -R galaxy:root \
        /etc/galaxy \
        /usr/share/galaxy \
        /var/lib/galaxy \
        /var/run/galaxy \
        /var/tmp/galaxy \
    && chmod -R u=rwX,g=rwX\
        /etc/galaxy \
        /usr/share/galaxy \
        /var/lib/galaxy \
        /var/run/galaxy \
        /var/tmp/galaxy

VOLUME ["/var/lib/galaxy", "/var/tmp/galaxy"]

WORKDIR /var/lib/galaxy

ENV DJANGO_SETTINGS_MODULE galaxy.settings.production
# Workaround for git running under different users
# See https://github.com/jenkinsci/docker/issues/519
ENV GIT_COMMITTER_NAME 'Ansible Galaxy'
ENV GIT_COMMITTER_EMAIL 'galaxy@ansible.com'

USER galaxy
EXPOSE 8000

ENTRYPOINT ["/entrypoint"]
CMD ["run", "web"]
