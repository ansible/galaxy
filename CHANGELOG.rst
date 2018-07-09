Ansible Galaxy Changes by Release
=================================

3.1.0 - Active development
--------------------------

3.0.2 - Release 03-Jul-2018
---------------------------

Bug Fixes
`````````
- Prevent existing repositories from being renamed with '-' converted to '_'
- Stop failng imports for lint warnings
- Revert namespace changes, where '-' was converted to '_' for existing namespaces.  

Closed PRs
``````````
- `825 Disable mandatory linting <https://github.com/ansible/galaxy/pull/825>`_
- `821 Fix APB name parse <https://github.com/ansible/galaxy/pull/821>`_
- `820 Revert replacing underscores with dashes in existing namespaces <https://github.com/ansible/galaxy/pull/820>`_
- `806 Prevent rename of exisiting repos <https://github.com/ansible/galaxy/pull/806>`_


3.0.1 - Released 03-Jul-2018 
----------------------------

Bug Fixes
`````````
- Removed Partner menu 
- Fixed Sort dropdown not populating on Search page  
- Perform case insensitive matching on Platforms during import
- Fixed duplicate key error happening on imports when existing Repository object not found 
- Fixed creation of new Repository objects when existing object not found, which was causing some existing roles to be renamed with '-' converted to '_' 
- Enable Galaxy Admins to start an import on any repository 
- Change filter on My Imports page to match exact user namespace
- Perform case insensitive match when installing roles using ``ansible-galaxy`` CLI
- Fixes broken ``ansible-galaxy search``, when using keywords
- Fix broken polling on My Imports page
- Add tooltip to import status on My Content page 
- Add missing logging messages to the API and UI 
- Fixed missing API response data that contributed to ``ansible-galaxy import`` breaking in Ansible 2.7.0
- Provide missing page titles in docs

Closed PRs
``````````
- `803 Fix broken client search <https://github.com/ansible/galaxy/pull/803>`_
- `801 Docs: Add missing page titles <https://github.com/ansible/galaxy/pull/801>`_
- `797 Partial fix for #796 <https://github.com/ansible/galaxy/pull/797>`_
- `792 Use INFO level for import log messages <https://github.com/ansible/galaxy/pull/792>`_
- `790 Perform case insensitive platform match <https://github.com/ansible/galaxy/pull/790>`_
- `789 Fix My Import polling <https://github.com/ansible/galaxy/pull/789>`_
- `788 Exact namespace filter on My Imports <https://github.com/ansible/galaxy/pull/788>`_
- `787 Case insensitive lookup on Namespace <https://github.com/ansible/galaxy/pull/787>`_
- `784 Fix Content Creation Error <https://github.com/ansible/galaxy/pull/784>`_
- `778 Allow admins to import any role <https://github.com/ansible/galaxy/pull/778>`_
- `772 Disable Partner menu <https://github.com/ansible/galaxy/pull/772>`_
- `771 Populate sort dropdown on Search page <https://github.com/ansible/galaxy/pull/771>`_

3.0.0 - Released 30-Jun-2018
----------------------------
- Move deployment of the public site from EC2 to OpenShift Dedicated
- Refactor the import process to support multiple static analysis tools, and to support future content testing
- Enforce Semantic Version format for git tags to be imported as versions
- Enforce Python compatability for new namespaces
- Add the ability to import multi-content repositories. Will only turn on multi-role support for 3.0.
- Add ability to import [Ansible Playbook Bundles (APBs)](https://github.com/ansibleplaybookbundle)
- Add database and API support for vendor namespaces, multi-role repositories, Ansible Playbook bundles (APBs), and multiple public source code management platforms
- Modernize the user interface (UI), including the implementation of Patternfly
- Add UI features to enable Galaxy admins to create and modify namespaces
- Add UI features that enable namespace owners to modify and maintain their namespaces
- Add UI features to support multi-role repositories, and new content types including APBs
- Remove and replace Elasticsearch with Postgres full-text search
- Rank search results by a calculated Best Match score that combines matched filters + download count
- Upgrade to Django 1.11, and begin adding Python 3 support
- Added doc site
