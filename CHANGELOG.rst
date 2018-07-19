Ansible Galaxy Changes by Release
=================================

3.1.0 - Active development
--------------------------

3.0.3 - Released 20-Jul-2018
----------------------------

Bug Fixes
`````````
- Improve mobile view of home, search, and author detail pages.
- For missing import date on search results, bypass call to moment.js.
- Add JS source maps to enable better debugging and troubleshooting.
- Fix partner carousel template on landing page.
- Add Nginx redirects for '/docs' and '/intro', redirecting to '/docs/'.
- Prevent random tag being added to search params during navigation. Issue `#809 <https://github.com/ansible/galaxy/issues/809>`_.
- During import process, default to the repository default branch, not 'master'. Issue `#857 <https://github.com/ansible/galaxy/issues/857>`_.
- Fix JS error that prevented removal of existing Namespace owners and provider namespaces.
- Limit repository attributes (i.e. commit message, description, etc.) to 256 chars.
- For content details, show the git tag value, rather than the strict semantic format value.
- Show Red Hat logo On production docs site.
- Document git tag version requirements.
- On search page, enable right-click on links, adjust icon sizing, fix confusing hover
  styles, fix ordering of cloud platforms. Issues: `#744 <https://github.com/ansible/galaxy/issues/744>`_, `#720 <https://github.com/ansible/galaxy/issues/720>`_, `#812 <https://github.com/ansible/galaxy/issues/812>`_, `#813 <https://github.com/ansible/galaxy/issues/813>`_, `#817 <https://github.com/ansible/galaxy/issues/817>`_.
- Fix broken 'Community' link on content detail page. Issue `#850 <https://github.com/ansible/galaxy/issues/850>`_.

Closed PRs
``````````
- `930 Fix Nginx static route <https://github.com/ansible/galaxy/pull/930>`_ 
- `913 Merge pull request #912 from newswangerd/author-detail-extravaganza-r <https://github.com/ansible/galaxy/pull/913>`_
- `910 Author detail extravaganza <https://github.com/ansible/galaxy/pull/910>`_
- `880 Add regex to check if dates are valid before passing to moment. <https://github.com/ansible/galaxy/pull/880>`_
- `877 Responsive search <https://github.com/ansible/galaxy/pull/877>`_
- `872 Generate source maps during build <https://github.com/ansible/galaxy/pull/872>`_
- `871 Should be ng-template <https://github.com/ansible/galaxy/pull/871>`_
- `864 Fix nginx redirects <https://github.com/ansible/galaxy/pull/864>`_
- `863 Fix tagging issue on search page. <https://github.com/ansible/galaxy/pull/863>`_
- `862 Make home page more responsive <https://github.com/ansible/galaxy/pull/862>`_
- `858 Use only default branch for import <https://github.com/ansible/galaxy/pull/858>`_
- `847 Fixes broken owner removal <https://github.com/ansible/galaxy/pull/847>`_
- `845 Limit Repository char fields to 256 chars <https://github.com/ansible/galaxy/pull/845>`_
- `844 Show version tag <https://github.com/ansible/galaxy/pull/844>`_
- `842 Fix docs logo <https://github.com/ansible/galaxy/pull/842>`_
- `838 Add version requirements to docs <https://github.com/ansible/galaxy/pull/838>`_
- `836 Use default cursor for tag hover <https://github.com/ansible/galaxy/pull/836>`_
- `835 Add 'name' to order_by params <https://github.com/ansible/galaxy/pull/835>`_
- `834 Fix broken community link <https://github.com/ansible/galaxy/pull/834>`_
- `833 Fix search links and icon sizing <https://github.com/ansible/galaxy/pull/833>`_

3.0.2 - Released 03-Jul-2018
----------------------------

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
