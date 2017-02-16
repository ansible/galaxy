# EC2 Deployment

The Galaxy infrastructure is deployed on EC2, and here you will find all the playbooks used to provision and configure it.

## Playbooks

Playbooks are listed in this section according to the order in which they are run to provision the infrastucure and deploy Galaxy. We provide a description for each playbook, along with a sample section to add to the variable file you'll pass to each playbook.

As you go through the examples below and build up your variable file, it will contain sensitive information, including usernames and passwords. For this reason, we recommend you use [Ansible Vault](http://docs.ansible.com/ansible/playbooks_vault.html) to encrypt it, and use either the `--ask-vault-pass` or `--vault-password-file` Ansible Playbook options to decrypt it at run-time. 

### create-galaxy-ec2.yml

Provisions a set of VMs used to host galaxy.

Prior to running this playbook, you'll need the following:

- pip install boto
- set AWS_ACCESS_KEY and AWS_SECRET_KEY in your environment
- Follow the [Create a VPC with a single public subnet tutorial](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Scenario1.html), to setup a VPC, two public subnets, and a security group
- Create an An SSH key pair EC2 
- A variable file that holds configuration options (an example is provided below)

Here's the sample variable file to hold configuration settings:

```
---
# The name of your security group
galaxy_group: galaxy-prod

# The AWS region to use
galaxy_region: us-east-1

# The IDs of your subnets
galaxy_subnets: 
 - subnet-144fd828
 - subnet-d3727a9a

# The name of a key pair stored on EC2 
galaxy_key_name: chouse

# Enable instance termination protection
galaxy_termination_protection: no

# The variable file that defines the set hosts that create-galaxy-ec2.yml will create
galaxy_hosts_definition: prod-hosts-definition.yml

# Establish variable names for tag group names returned by ec2.py
galaxy_hosts_all: tag_galaxy_prod
galaxy_hosts_db: tag_galaxy_group_pr_db
galaxy_hosts_web: tag_galaxy_group_pr_web
galaxy_hosts_elastic: tag_galaxy_group_pr_elastic
galaxy_hosts_celery: tag_galaxy_group_pr_celery
```

Running the playbook will create all of the hosts defined in the `prod-hosts-definition.yml` file, which is referenced by the variable `galaxy_hosts_definition`. Obviously, you will want to review this file, and adjust it to fit your needs. It's setup to create two web servers hosts, two database hosts, three elasticsearch hosts, and three celery hosts; splitting the hosts across the two subnets.

All nodes are taged with `galaxy:prod`. Each node is then given a group tag of `galaxy_group:<group>`, where group is one of: pr_db, pr_elastic, pr_web, pr_celery. The remaining playbooks rely on the ec2.py inventory script to dynamically pull the inventory from EC2, and group nodes by these tag values. A copy of the inventory script is included in this directory for convenience.

Here's an example of how to run the playbook, passing in a custom vars file:

```
$ ansible-playbook --extra-vars="@your-vars-file.yml" create-galaxy-ec2.yml
```

### init-galaxy-ec2.yml

Installs and configures `ntp`, creates users, adds each user's public SSH key(s) to the there account's `authorized_keys` file, and updates the sudoers file, so that a password is not required to use `sudo`. If there are other initial config actions you want to perform on the newly created nodes, this is a good place to do it. 

Prior to running the playbook, you'll need to create your own `authorized-users.yml` file to defined `authorized_users` as follows: 

```
authorized_users:
- username: dsmith 
  github_user: dsmith-001 
- username: jcinclair
  github_user: jimicinc
```

The `username` is the user account that will be created on each node, and `github_user` provides the source for the user's public SSH keys.

The following is an example of how to run the playbook:

```
$ ansible-playbook -i ec2.py --user centos --extra-vars="@your-vars-file.yml" init-galaxy-ec2.yml
``` 

Notice it's using the `ec2.py` inventory script to dynamically retreive the set of nodes from EC2. Tasks will execute on hosts included in the `galaxy_hosts_all` group defined in your variable file. See the example above.

Nodes are created using a centos:7 AMI, which by default creates a `centos` user. Once you've created your user accounts, and verified that your SSH keys are working as expected, you may want to remove the `centos` user. 

### config-galaxy-ec2.yml

Install packages, and perform general configuration of each node according to its group assignment. 

Prior to running, you'll want to add the following to your variable file:

```
# postgresql
#  Subnets allowed to access the database
galaxy_subnet_cidrs:
  - 10.0.10.0/24
  - 10.0.11.0/24

#  The galaxy user password
galaxy_postgresql_password: opensesame!

# rabbit
galaxy_rabbit_username: galaxy
galaxy_rabbit_password: <your database password> 

# web
#  SMTP connection info for sending email
galaxy_email_hostname: smtp.email-server.com
galaxy_email_port: 587 
galaxy_email_username: emailuser 
galaxy_email_password: password 

#  Where to send email, when a 500 server error occurs
galaxy_admins: "('Dave', 'dsmith@email.company.com>'), ('Bob', bbobsworth@email.company.com)"

#  The DNS name mapped to the web servers.
galaxy_site_name: galaxy.acme.com

# Database replication user and password
galaxy_replicator_user: replicator
galaxy_replicator_pass: mysecret! 
```

The following provides an example of how to run the playbook:

```
ansible-playbook -i ec2.py --extra-vars="@your-vars-file.yml" config-galaxy-ec2.yml
```

### deploy-galaxy-ec2.yml

Deploy the galaxy appliction to the nodes in the web and celery groups.

Prior to running, you'll need to add the following to your variable file:

```
# GitHub user accounts for accessing the GitHub API
github_task_users: []

# Update galaxy/templates/robots.txt to disallow searchbots
galaxy_disallow_searchbots: yes

# Make it a little harder to find the django admin site
galaxy_admin_url: link__to__your__admin_site
```

For `github_task_users` provide a list of GitHub user accounts to use for running administrative tasks. You'll need to manually create each account on GitHub, and then log into your instance of Galaxy using the account. You can create the accounts later. All that's needed at this point is a set of account names that you plan to create.

The list gets added to the `/etc/galaxy/settings.py` file on each node. It's specifically used by the `refresh_role_counts` management command. If you don't intend to run this command to keep to keep GitHub star and watch counts up to date in your Galaxy instance, you can leave the list empty.

The following provides an example of how to run the playbook:

```
$ ansible-playbook -i ec2.py --extra-vars="@your-var-file.yml" deploy-galaxy-ec2.yml 
```

The playbook will build the Galaxy distribution package, copy it to each node, install it, and then build the Elasticsearch indexes, which at this point will be empty, because no roles have been imported into your datbaase.

### create-elb-ec2.yml

Create an EC2 classic load balancer for your site, and add your web server nodes as instances.

Prior to running, you'll need to acquire an SSL certificate and upload it to AWS, and you'll need to create a new security group for use exclusively with the load balancer to allow inbound access to ports 80 and 443.

Once you have these items, add the following to your variable file:

```
# ELB
galaxy_elb_certificate: arn:aws:acm:us-east-1:XXXXXXXXX:certificate/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
galaxy_elb_name: galaxy-qa
galaxy_elb_security_groups:
- sg-23f1be5f
```

The following provides an example of how to run the playbook:

```
$ ansible-playbook -i ec2.py --extra-vars="@your-vars-file.yml" create-elb-ec2.yml
```

### remove_galaxy_ec2.yml

As the name suggests, removes all of the ec2 nodes. It relies on the `ec2.py` inventory script, and removes anything found the group associated with `galaxy_hosts_all` in your variable file. 

Prior to running this playbook, log into the EC2 console, and turn off the `termination protection` setting on any instances where it is enabled.

Here's an example of how to run the playbook:

```
$ ansible-playbook -i ec2.py --extra-vars="@your-vars-file.yml" remove-gaalaxy-ec2.yml
```


