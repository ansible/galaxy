%if 0%{?rhel} && 0%{?rhel} <= 5
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
%endif

Name: galaxy
Summary: Galaxy: API, UI and Task Engine for ansible-galaxy
Version: %(%{__python} -c "from galaxy import __version__; print(__version__.split('-')[0])")
Release: %{?_pkgrelease}%{dist}
Source0: https://github.com/downloads/ansible/galaxy/%{name}-%{version}.tar.gz

Group: Development/Libraries
License: GPLv3
Url: http://github.com/ansible/galaxy

BuildArch: noarch
%if 0%{?rhel} && 0%{?rhel} <= 5
BuildRequires: python26-devel
%else
BuildRequires: python-devel
%endif

# Requires: ansible
Requires: httpd
Requires: mod_wsgi
Requires: postgresql-server
Requires: python-psycopg2
Requires: python-setuptools
Requires: python-ldap
Requires: supervisor

%description

Galaxy - your hub for finding, reusing and sharing the best Ansible content. 


%prep
%setup -q

%build
%{__python} setup.py build egg_info -b ""

%install
%{__python} setup.py install --skip-build --root=$RPM_BUILD_ROOT egg_info -b ""
mkdir -p $RPM_BUILD_ROOT/etc/galaxy/

%post
if [ ! -f /etc/galaxy/SECRET_KEY ]; then
    %{__python} -c "import uuid; file('/etc/galaxy/SECRET_KEY', 'wb').write(uuid.uuid4().hex)"
fi
chown galaxy: /etc/galaxy/SECRET_KEY
chmod 400 /etc/galaxy/SECRET_KEY
/usr/bin/galaxy-manage collectstatic --noinput &> /dev/null

if ! grep -q '^# START GALAXY' /etc/supervisord.conf; then
cat<<'EOF'>>/etc/supervisord.conf
# START GALAXY CONFIG
[program:galaxy-celeryd]
autorestart = true
logfile = /var/log/supervisor/galaxy-celeryd.log
stopwaitsecs = 600
log_stdout = true
command = /usr/bin/galaxy-manage celeryd -B -l info --autoscale=20,2
user = galaxy
autostart = true
directory = /var/lib/galaxy
log_stderr = true
logfile_maxbytes = 50MB
logfile_backups = 999
environment=HOME=/var/lib/galaxy,USER=galaxy
# END GALAXY CONFIG
EOF
fi

%postun
sed -i -e '/^# START GALAXY/,/^# END GALAXY/d' /etc/supervisord.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group galaxy >/dev/null || groupadd -r galaxy
getent passwd galaxy >/dev/null || \
    useradd -r -g galaxy -d /var/lib/galaxy -s /bin/bash galaxy
exit 0

%files
%defattr(-,root,root)
%{python_sitelib}/galaxy*
%{_bindir}/galaxy-manage*
%config(noreplace) %{_sysconfdir}/httpd/conf.d/galaxy.conf
%defattr(-,galaxy,galaxy)
/var/lib/galaxy
%config(noreplace) %{_sysconfdir}/galaxy

%changelog

* Mon Dec 16 2013 James Laska <jlaska@ansibleworks.com>
- Initial RPM packaging for galaxy

