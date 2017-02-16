[![Build Status](https://travis-ci.org/chouseknecht/ansible-role-pgclone.svg?branch=master)](https://travis-ci.org/chouseknecht/ansible-role-sendmail)

pgclone
=======

Clone a PostgreSQL cluster from a remote host. Optionally creates a recovery.conf and puts the clone in standby mode.


Requirements
------------

Requires a running PostgreSQL cluster, and assumes PostgreSQL was previously installed on the target host.


Role Variables
--------------

pgbase_output_dir: /var/lib/pgsql/data
> Directory to wite the output to. Existing contents will be destroyed.

pgbase_create_recovery_file: yes
> Indicate whether or not to create recovery.conf file.

pgbase_standby_mode: off
> Set to 'on', if the clone will be started as a standby.

pgbase_connect_host: ''
> Name or IP address the primary database host.

pgbase_connect_port: 5432
> Connection port on the remote or masterdatabase host.

pgbase_connect_user: ''
> Username to use when connecting to the remote or master database. 

pgbase_connect_pass: ''
> Password for connecting to the remote or master database.

pgbase_trigger_file: /tmp/trigger
> Sets the trigger_file path in recovery.conf. When a trigger file is detected, the secondary database exits standby mode, and switches to normal operation.

pgbase_backup_dir: /tmp
> Path where backup files will be placed. 

pgbase_save_files: []
> List of files to backup before starting the backup process and removing pgbase_output_dir.


Dependencies
------------

None.


Example Playbook
----------------

- name: Clone the master database to the slave 
  hosts: secondary-db-host  
  become: yes
  vars:
  roles:
    - role: chouseknecht.pgclone 
      pgbase_output_dir: /var/lib/pgsql/data
      pgbase_backup_dir: /tmp

      # Recovery file options
      pgbase_create_recovery_file: True
      pgbase_standby_mode: "on"
      pgbase_trigger_file: "/tmp/trigger"

      # The remote host with the database we want to copy
      pgbase_connect_host: "{{ master_ip }}" 
      pgbase_connect_port: 5432
      pgbase_connect_user: "{{ replicator_user }}" 
      pgbase_connect_pass: "{{ replicator_pass }}" 

      # The data directory will be removed. Add to the list any files that should be saved. 
      pgbase_save_files:
      - pg_hba.conf
      - postgresql.conf

License
-------

MIT

Author Information
------------------

[@chouseknecht](https://github.com/chouseknecht)
