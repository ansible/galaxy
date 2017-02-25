Ansible Datadog Role
========
[![Ansible Galaxy](http://img.shields.io/badge/galaxy-Datadog.datadog-660198.svg)](https://galaxy.ansible.com/Datadog/datadog/)

Install and configure Datadog base agent & checks.

Supports most Debian and RHEL-based Linux distributions.

Installation
------------

```
ansible-galaxy install Datadog.datadog
```

Role Variables
--------------

- `datadog_api_key` - Your Datadog API key.
- `datadog_checks` - YAML configuration for agent checks to drop into `/etc/dd-agent/conf.d`.
- `datadog_config` - Settings to place in `/etc/dd-agent/datadog.conf`.
- `datadog_process_checks` - Array of process checks and options (DEPRECATED: use `process` under
`datadog_checks` instead)
- `datadog_apt_repo` - Override default Datadog `apt` repository
- `datadog_apt_key_url` - Override default url to Datadog `apt` key
- `datadog_apt_key_url_new` - Override default url to the new Datadog `apt` key (in the near future the `apt` repo will have to be checked against this new key instead of the current key)

Dependencies
------------
None

Example Playbooks
-------------------------
```
- hosts: servers
  roles:
    - { role: Datadog.datadog, become: yes }  # On Ansible < 1.9, use `sudo: yes` instead of `become: yes`
  vars:
    datadog_api_key: "123456"
    datadog_config:
      tags: "mytag0, mytag1"
      log_level: INFO
    datadog_checks:
      process:
        init_config:
        instances:
          - name: ssh
            search_string: ['ssh', 'sshd' ]
          - name: syslog
            search_string: ['rsyslog' ]
            cpu_check_interval: 0.2
            exact_match: true
            ignore_denied_access: true
      ssh_check:
        init_config:
        instances:
          - host: localhost
            port: 22
            username: root
            password: changeme
            sftp_check: True
            private_key_file:
            add_missing_keys: True
      nginx:
        init_config:
        instances:
          - nginx_status_url: http://example.com/nginx_status/
            tags:
              - instance:foo
          - nginx_status_url: http://example2.com:1234/nginx_status/
            tags:
              - instance:bar
```

```
- hosts: servers
  roles:
    - { role: Datadog.datadog, become: yes, datadog_api_key: "mykey" }  # On Ansible < 1.9, use `sudo: yes` instead of `become: yes`
```

License
-------

Apache2

Author Information
------------------

brian@akins.org

dustinjamesbrown@gmail.com --Forked from brian@akins.org

Datadog <info@datadoghq.com> --Forked from dustinjamesbrown@gmail.com
