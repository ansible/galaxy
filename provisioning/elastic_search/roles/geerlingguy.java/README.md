# Ansible Role: Java

[![Build Status](https://travis-ci.org/geerlingguy/ansible-role-java.svg?branch=master)](https://travis-ci.org/geerlingguy/ansible-role-java)

Installs Java for RedHat/CentOS and Debian/Ubuntu linux servers.

## Requirements

None.

## Role Variables

Available variables are listed below, along with default values:

    java_packages:
      - java-1.7.0-openjdk

Set the version/development kit of Java to install, along with any other necessary Java packages. Some other options include are included in the distribution-specific files in this role's 'defaults' folder.

## Dependencies

None.

## Example Playbook

    - hosts: servers
      roles:
        - { role: geerlingguy.java }

## License

MIT / BSD

## Author Information

This role was created in 2014 by [Jeff Geerling](http://jeffgeerling.com/), author of [Ansible for DevOps](http://ansiblefordevops.com/).
