FROM galaxy-build

LABEL com.ansible.galaxy.description="Ansible Galaxy development"

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

COPY scripts/docker-dev/entrypoint.sh /entrypoint.sh

WORKDIR /galaxy
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/galaxy/scripts/docker-dev/start-develop.sh"]
