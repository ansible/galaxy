FROM galaxy-base:latest

# Install node.js and yarn
RUN curl -sL -o '/tmp/nodesource-release-el7-1.noarch.rpm' \
        'https://rpm.nodesource.com/pub_8.x/el/7/x86_64/nodesource-release-el7-1.noarch.rpm' \
    && rpm -i --nosignature --force '/tmp/nodesource-release-el7-1.noarch.rpm' \
    && rm -f '/tmp/nodesource-release-el7-1.noarch.rpm' \
    && curl -sL -o '/etc/yum.repos.d/yarn.repo' 'https://dl.yarnpkg.com/rpm/yarn.repo' \
    && yum -y install nodejs yarn \
    && yum -y clean all \
    && rm -rf /var/cache/yum

RUN mkdir -p /galaxy
COPY . /galaxy
WORKDIR /galaxy

RUN /galaxy/scripts/docker/release/build.sh
