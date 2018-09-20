Ansible Galaxy Changes by Release
=================================

3.1.0 - Active development
--------------------------

3.0.11 - Released 20-Sep-2018
-----------------------------

Changes
```````
- Search results return irrelevant content. Issue `1024 <https://github.com/ansible/galaxy/issues/1024>`_.
- Remove unnecessary query for partner content during search page load.

Closed PRs
``````````
- `1146 Fix ranking getting set to 0 <https://github.com/ansible/galaxy/pull/1146>`_.
- `1149 Refactor default parameters on search page <<https://github.com/ansible/galaxy/pull/1146>`_.

3.0.10 - Released 12-Sep-2018
-----------------------------

Changes
```````
- Deploy search metrics collection to production. Issue `1105 <https://github.com/ansible/galaxy/issues/1105>`_.

Closed PRs
``````````
- `1135 Add search metrics support <https://github.com/ansible/galaxy/pull/1135>`_.
- `1136 Enable Django Prometheus middleware <https://github.com/ansible/galaxy/pull/1136>`_.
- `1137 Tune Gunicorn for production image <https://github.com/ansible/galaxy/pull/1137>`_.
- `1139 Change metrics URL to /metrics <https://github.com/ansible/galaxy/pull/1139>`_.
- `1141 Add prefixes to Galaxy search metrics <https://github.com/ansible/galaxy/pull/1141>`_

3.0.9 - Released 05-Sep-2018
----------------------------

Bug Fixes
`````````
- Root path redirecting to Login page, rather than Home. Issue `1120 <https://github.com/ansible/galaxy/issues/1120>`_.

Closed PRs
``````````
- `1126 Insure /home is the default route <https://github.com/ansible/galaxy/pull/1126>`_.

3.0.8 - Released 22-Aug-2018
----------------------------

Bug Fixes
`````````
- Made the help link more obvious, and added a link to the Galaxy project issue queue. Issue `1006 <https://github.com/ansible/galaxy/issues/1006>`_.
- Upgraded to latest version of patternfly-ng. Issue `1010 <https://github.com/ansible/galaxy/issues/1010>`_.
- Fixed issues related to patternfly-ng upgrade.
- Limited display of container logs in Travis CI builds.
- Added support for travis-ci.com server. Issue `1033 <https://github.com/ansible/galaxy/issues/1033>`_.
- Improved Galaxy server side logging.
- Set the avatar URL attribute during Provider Namespace creation.
- Added AnsibleFest 2018 image to the home page.
- Reformatted APB parameter metadata.
- Implemented prettier to enforce Typescript and Less code formatting.
- Improved TypeScript linting.

Closed PRs
``````````
- `1084 Prevent queries on sensitive fields #1084 <https://github.com/ansible/galaxy/pull/1084>`_
- `1070 Fix spacing issues introduced by patternfly update <https://github.com/ansible/galaxy/pull/1070>`_
- `1069 Added help link which links to the github issues <https://github.com/ansible/galaxy/pull/1069>`_
- `1066 Add spinner to indicate when page is loading. <https://github.com/ansible/galaxy/pull/1066>`_
- `1065 Fix about modal. <https://github.com/ansible/galaxy/pull/1065>`_
- `1064 Fix patternfly error messages. <https://github.com/ansible/galaxy/pull/1064>`_
- `1060 Fix make dev/log (#1041) <https://github.com/ansible/galaxy/pull/1060>`_
- `1058 Support multiple Travis CI servers <https://github.com/ansible/galaxy/pull/1058>`_
- `1057 Release/3.0.8 request id logging <https://github.com/ansible/galaxy/pull/1057>`_
- `1053 Make documentation link more visible. <https://github.com/ansible/galaxy/pull/1053>`_
- `1051 Set ProviderNamespace.avatar_url (#1035) <https://github.com/ansible/galaxy/pull/1051>`_
- `1050 Updated galaxy team <https://github.com/ansible/galaxy/pull/1050>`_
- `1044 Upgrade to latest patternfly-ng <https://github.com/ansible/galaxy/pull/1044>`_
- `1027 Reformat some APB parameter metadata on save <https://github.com/ansible/galaxy/pull/1027>`_
- `1023 Enforce TypeScript and Less code formatting with prettier.  <https://github.com/ansible/galaxy/pull/1023>`_
- `1021 Disable lazy loading on my content <https://github.com/ansible/galaxy/pull/1021>`_
- `1020 Remove TS unused variables  <https://github.com/ansible/galaxy/pull/1020>`_
- `1019 Fix license in galaxyui package.json <https://github.com/ansible/galaxy/pull/1019>`_
- `1018 Enable no-consecutive-blank-lines rule <https://github.com/ansible/galaxy/pull/1018>`_
- `1017 Enable tslint interface-name rule <https://github.com/ansible/galaxy/pull/1017>`_
- `1016 Enable prefer-for-of in tslint <https://github.com/ansible/galaxy/pull/1016>`_
- `1015 Backport/866 tslint recommend <https://github.com/ansible/galaxy/pull/1015>`_
- `1014 Backport/739 lazy loading <https://github.com/ansible/galaxy/pull/1014>`_

3.0.7 - Released 09-Aug-2018
----------------------------

Bug Fixes
`````````
- Removed featured icon from home page.

Closed PRs
``````````
- `1036 Remove featured icon from home page <https://github.com/ansible/galaxy/pull/1037>`_.

3.0.6 - Released 09-Aug-2018
----------------------------

Bug Fixes
`````````
- Travis CI notification not triggering an import. Issue `#1033 <https://github.com/ansible/galaxy/issues/1033>`_.

Closed PRs
``````````
- `1036 Restore GITHUB_TASK_USERS <https://github.com/ansible/galaxy/pull/1036>`_

3.0.5 - Released 03-Aug-2018
----------------------------

Bug Fixes
`````````
- Fixed broken error handling on home page, when 500 errors arise from the Namespace resource. Issue `#981 <https://github.com/ansible/galaxy/issues/981>`_.
- Fixed stacktrace on My Content page.
- Added Developer's Guide to Galaxy docs.
- Added required packages, `gcc` and `python-devel`, to release build process
- On Search and Community pages, added automatic scroll to the top of the page after navigating to next page. Issue `#750 <https://github.com/ansible/galaxy/issues/750>`_.
- On an authors page, added ability to sort by forks, stargazers, downloads and watchers. Issue `#965 <https://github.com/ansible/galaxy/issues/965>`_.
- Updated install and usage docs for `Mazer <https://github.com/ansible/mazer>`_. Mazer issue `#106 <https://github.com/ansible/mazer/issues/106>`_.
- Applied style fixes to Role README display. Issue `#718 <https://github.com/ansible/galaxy/issues/718>`_.
- Fixed copy-to-clipboard styling. Issue `#722 <https://github.com/ansible/galaxy/issues/722>`_.
- Applied style fixes to Content Detail page. Issue `#722 <https://github.com/ansible/galaxy/issues/722>`_.
- Improved breadcrumb styling on mobile screens. Issue `#718 <https://github.com/ansible/galaxy/issues/722>`_.
- Improved documentation for `role_name`. Issue `#939 <https://github.com/ansible/galaxy/issues/939>`_.
- Fixed search page parameter error. Issue `#919 <https://github.com/ansible/galaxy/issues/919>`_.
- Fixed image sizing on Content Detail and Search pages. Issues `#934 <https://github.com/ansible/galaxy/issues/934>`_ and `#927 <https://github.com/ansible/galaxy/issues/927>`_.
- Fixed tooltip flicker on Travis icons. Issue `#938 <https://github.com/ansible/galaxy/issues/932>`_.
- Added pagination and filtering on My Content repositories list. Issue `#582 <https://github.com/ansible/galaxy/issues/582>`_ and `#935 <https://github.com/ansible/galaxy/issues/935>`_.

Closed PRs
``````````
- `1002 Fix broken error handling <https://github.com/ansible/galaxy/pull/1002>`_
- `1001 Fix stack trace on my-content page <https://github.com/ansible/galaxy/pull/1001>`_
- `997 Add developer's guides <https://github.com/ansible/galaxy/pull/997>`_
- `996 Install required packages when building release image <https://github.com/ansible/galaxy/pull/996>`_
- `987 Make pages scroll to top when they are loaded <https://github.com/ansible/galaxy/pull/987>`_
- `972 mazer_role_loader docs for galaxy.ansible.com/docs <https://github.com/ansible/galaxy/pull/972>`_
- `970 Read me button and tag style fixes <https://github.com/ansible/galaxy/pull/970>`_
- `969 Added option to filter by download, star, watcher and fork count on a… <https://github.com/ansible/galaxy/pull/969>`_
- `964 Style upgrades to clipboard <https://github.com/ansible/galaxy/pull/964>`_
- `961 Improve breadcrumbs <https://github.com/ansible/galaxy/pull/961>`_
- `958 Fix description and minor style issues on author detail page. <https://github.com/ansible/galaxy/pull/958>`_
- `952 Improve doc for role_name and Git-installed roles <https://github.com/ansible/galaxy/pull/952>`_
- `940 Convert page URL parameters to integers on search page. <https://github.com/ansible/galaxy/pull/940>`_
- `938 Fix tooltip flicker on travis icons <https://github.com/ansible/galaxy/pull/938>`_
- `937 Prevent images on content detail from getting stretched out <https://github.com/ansible/galaxy/pull/937>`_
- `931 Prevent search images from stretching out <https://github.com/ansible/galaxy/pull/931>`_
- `928 Add pagination and searching repositories on My Content page <https://github.com/ansible/galaxy/pull/928>`_


3.0.4 - Released 30-Jul-2018
----------------------------

Bug Fixes
`````````
- Fixed 500 errors resulting from the maximum number of database connections being reached. Issue `#977 <https://github.com/ansible/galaxy/issues/977>`_.

Closed PRs
``````````
- `986 Disable Django persistent connections <https://github.com/ansible/galaxy/pull/986>`_
- `984 Limit persistent connection lifetime <https://github.com/ansible/galaxy/pull/984>`_


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
