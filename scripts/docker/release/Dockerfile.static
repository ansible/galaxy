# vim: set ft=Dockerfile:
FROM centos:7

ENV NGINX_ROOT=/etc/opt/rh/rh-nginx112/nginx

RUN yum install -y centos-release-scl-rh \
    && yum -y install --setopt=tsflags=nodocs rh-nginx112 rh-nginx112-nginx \
    && yum -y clean all \
    && rm -rf /var/cache/yum

COPY scripts/docker/release/nginx/default.conf /etc/opt/rh/rh-nginx112/nginx/conf.d/default.conf
COPY scripts/docker/release/nginx/nginx.conf /etc/opt/rh/rh-nginx112/nginx/nginx.conf
RUN chmod g+w /var/opt/rh/rh-nginx112/run/nginx \
    && chown -R nginx:root /var/opt/rh/rh-nginx112/ \
    && chmod -R g+rwx /var/opt/rh/rh-nginx112/

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/opt/rh/rh-nginx112/log/nginx/access.log \
    && ln -sf /dev/stderr /var/opt/rh/rh-nginx112/log/nginx/error.log

EXPOSE 8000

STOPSIGNAL SIGTERM

USER nginx

CMD ["/opt/rh/rh-nginx112/root/usr/sbin/nginx", "-g", "daemon off;"]

COPY --from=galaxy-build:latest /galaxy/build/static /opt/rh/rh-nginx112/root/usr/share/nginx/html
