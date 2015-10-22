pgclone
=======

Use pgclone to clone a PostgreSQL cluster from a remote host. Optionally create a recovery.conf and 
put the clone in standby mode.


Requirements
------------

Requires a running PostgreSQL cluster and assumes PostgreSQL is installed on the target host.


Role Variables
--------------

pgbase_output_dir - Directory to wite the output to. Existing contents will be destroyed.

pgbase_service_name - Name of the systemd postgresql service, typically "postgresql".

pgbase_create_recover_file - True, if recovery.conf should be created.

pgbase_standby_mode - Set to 'on', if the clone will be started as a standby.

pgbase_connect_host - Name or IP address the primary database host.

pgbase_connect_port - Connection port on the primary database host.

pgbase_connect_user - PostgreSQL username to use when connecting to the primary database. 

pgbase_connect_pass - Password for connecting to the primary database.

pgbase_trigger_file - Path of trigger file used to end recover in standby mode.

pgbase_backup_dir - Path where backup files will be kept. 

pgbase_save_files - Array of files to backup prior to starting the backup process. 


Dependencies
------------

None.


Example Playbook
----------------
A simple playbook would be: 

    - hosts: servers
      roles:
          - { role: chouseknecht.pg_basebackup }

However, most fo the variables do not have default values, as many of them are project specific things like username and password. It might be best to store these items using vault. Nonsecure items could be placed in playbook vars or in a separate vars file. So your playbook might look more like this:

   - hosts: servers
     vars:
         pgbase_trigger_file: "foo" 
         pgbase_connect_port: 5432
         pgbase_connect_host: 1.2.3.4
         pgbase_standby_mode: "on"
         pgbase_create_recover_file: True
     vars_files:
         - project-vault.yml
     roles:
         - { role: chouseknecht.pg_basebackup }

License
-------

MIT

Author Information
------------------

Chris Houseknecht

chouseknecht at ansible.com
