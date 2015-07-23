ntp
===

This role enables users to install and configure ntp on their hosts.

Requirements
------------

This role requires Ansible 1.4 or higher, and platform requirements are listed
in the metadata file.

Role Variables
--------------

The variables that can be passed to this role and a brief description about
them are as follows. See the NTP configuration documentation for details:

	# The driftfile
	ntp_driftfile: /var/lib/ntp/drifta

	# The server to sync time with
	ntp_server: [0.ubuntu.pool.ntp.org, 1.ubuntu.pool.ntp.org]

	ntp_restrict:                                                           
	  - "restrict -4 default kod notrap nomodify nopeer noquery"
	  - "restrict -6 default kod notrap nomodify nopeer noquery"
	  - "restrict 127.0.0.1"

	ntp_crypto: no
	ntp_includefile: no
	ntp_keys: no
	ntp_trustedkey: no
	ntp_requestkey: no
	ntp_controlkey: no
	ntp_statistics: no
	ntp_broadcast: no
	ntp_broadcastclient: no
	ntp_multicastclient: no

Examples
--------

1) Install ntp and set the default settings.

	- hosts: all
	  roles:
	    - role: ntp

2) Install ntp and set some custom servers.

	- hosts: all
	  roles:
	    - role: ntp
	      ntp_server: [2.ubuntu.pool.ntp.org, 1.ubuntu.pool.ntp.org]

Dependencies
------------

None

License
-------

BSD

Author Information
------------------

Benno Joy

