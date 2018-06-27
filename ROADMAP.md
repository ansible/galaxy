# Roadmap

## Release 3.0
Target release date: 30 June 2018

- Move deployment of the public site from EC2 to OpenShift Dedicated
- Refactor the import process to support multiple static analysis tools, and to support future content testing
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

## Release 2.4 (Completed)

- Determine scope of supporting private GitHub repos [#161](https://github.com/ansible/galaxy/issues/161)
- Add OpenShift as an install option [#160](https://github.com/ansible/galaxy/issues/160)
- Role type indicator [#158](https://github.com/ansible/galaxy/issues/158)
- Cloud platforms [#157](https://github.com/ansible/galaxy/issues/157)
- Dynamic home page content [#156](https://github.com/ansible/galaxy/issues/156) 
- Download button [#155](https://github.com/ansible/galaxy/issues/156)
- Make it easier to know 'role relavance' [#36](https://github.com/ansible/galaxy/issues/36)

## Release 2.3 (Completed)

- Cleanup and simplify the development container build and run workflow
- Create a container release workflow that results in pre-baked images hosted on Docker Hub
- Create a simple installer, similar to AWX, that deploys pre-baked Galaxy images to Docker and OpenShif. See [PR #118](https://github.com/ansible/galaxy/pull/118)
- Start a framework for backend testing [#37](https://github.com/ansible/galaxy/issues/37)
- Fix [#38](https://github.com/ansible/galaxy/issues/38), 404 page for roles uses 200 status header
- Fix [#47](https://github.com/ansible/galaxy/issues/47), no error when adding a new role/container project that has the same name as an existing project
- Support adding embedded video to the detail page of a 'role' via meta data. Landed in [PR #94](https://github.com/ansible/galaxy/pull/94)


