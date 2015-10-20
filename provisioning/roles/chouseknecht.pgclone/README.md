pgclone
=======

Use pg_basebackup to clone a PostgreSQL cluster from a remote host. Optionally create a recover.conf and 
put the clone in standby mode.


Requirements
------------

Requires a running PostgreSQL cluster and assumes PostgreSQL is installed on the target host.


Role Variables
--------------

pgbase_output_dir - Directory to wite the output to. Existing contents will be destroyed.

pgbase_host - Host of the existing PostgreSQL cluster.  

pgbase_username - PostgreSQL role used to connect to the existing PostgreSQL cluster.

pgbase_create_recover_file - True, if recover.conf should be created.

pgbase_standby_mode - Set to 'on', if the clone will be started as a standby.

pgbase_connect_host - Primary host to connect to when in standby mode.

pgbase_connect_port - Port to connection on when in standby mode.

pgbase_connect_user - Username for standby mode connection.

pgbase_connect_pass - Password for standby mode connection.

pgbase_trigger_file - Path of trigger file used to end recover in standby mode.

pgbase_backup_dir - Path where backup files will be kept. 

pgbase_save_files - Array of files to backup prior to starting the backup process. 


Dependencies
------------

None.


Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: chouseknecht.pg_basebackup }

License
-------

MIT

Author Information
------------------

Chris Houseknecht

chouseknecht at ansible.com
