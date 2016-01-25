# Galaxy 2.0.0 Test Plan

## Features Tested

### Migration of Existing Roles Where github_user != namespace

- [ ]  Find role using the pre-migration namespace
- [ ]  Using the role as a dependency works
- [ ]  Installing the role works
- [ ]  Re-importing the role does not change the namespace
- [ ]  Deleting and importing the role moves the role to github_user namespace
- [ ]  
  
### Manage Roles

- [ ]  All user role repositories listed on My Roles page.
- [ ]  Only repos containing a role (defined by existing of meta/main.yml) appear on My Roles page.
- [ ]  Moving the switch to On imports the role
- [ ]  During import process spinner to the right of the switch is active
- [ ]  During import process switch is inactive
- [ ]  Turning the switch to the Off position deletes the role
- [ ]  During role deletion the spinner to the right of the switch is active
- [ ]  During role deletion the switch is inactve
- [ ]  Clicking the gear next to the role shows a drop down with form for Travis token 
- [ ]  Can add a Travis token
- [ ]  Can update a Travis token
- [ ]  Can remove a Travis token
- [ ]  Search box correctly filters the list
- [ ]  Refresh re-builds the list from GitHub
- [ ]  Clicking role name takes you to role details
- [ ]  Page is responsive to tablet and phone sizes
 
### My Imports

- [ ]  Latest import for each role appears (only for imports occurring after 2.0 deployment)
- [ ]  Clicking on a role shows the related details
- [ ]  Clicking re-import initiates an import
- [ ]  Clicking re-import causes the new import to appear in the details
- [ ]  Most recent commit SHA and message shown
- [ ]  Most recent stargazer, watcher and fork counts are accurate
- [ ]  Search box correctly filters list
- [ ]  Last runtime is correct
- [ ]  Last runtime updates on each page refresh
- [ ]  Clicking on role name (on right top-right) takes you to role details
- [ ]  Clicking Add button takes you to My Roles page
- [ ]  Page responsive to tablet and phone sizes
 
### Browse Roles

- [ ]  Search by Keyword returns expected results
- [ ]  Search by Tags returns expected results
- [ ]  Search by Platforms returns expected results
- [ ]  Search by Author return expected results
- [ ]  Sort by Relavance works
- [ ]  Sort by Name works
- [ ]  Sort by Author works
- [ ]  Sort by Created works 
- [ ]  Sort by Stargazers works
- [ ]  Sort by Watchers
- [ ]  Sort by Downloads
- [ ]  Popular tags list populates and is sorted by descending role count
- [ ]  Page responsive to tablet and phone sizes
 
### Install Role - CLI
- [ ]  Role installed to roles_path as expected
- [ ]  Dependencies installed to roles_path as expected
- [ ]  Download count for the role and each dependency increment by 1

### Remove Role - CLI
- [ ]  Role is removed from the roles_path

### Re-install Role - CLI
- [ ]  Role and dependencies re-install
- [ ]  Download counts for each role do not increment and remain the same.

### Delete Role - CLI
- [ ]  Role is deleted from Galaxy database (verify using /v1/api/roles)
- [ ]  Role no longer returned on Browse Roles page

### Import Role with Travis
- [ ]  Triggering Travis build results in an import running on Galaxy
- [ ]  Correct Tavis build status shows on My Imports page
- [ ]  Correct Travis build status shows on B
 
 

### Travis Integration - web site 

### Travis Integration with Branch Option - CLI

### Login - CLI

### Import - CLI

### Delete - CLI

### Search - CLI

### Install - CLI

### Info - CLI

