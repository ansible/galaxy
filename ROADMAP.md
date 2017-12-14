# Roadmap

## [Release 2.4.1](https://github.com/ansible/galaxy/milestone/4) (Current development)

- Search page re-design. [#185](https://github.com/ansible/galaxy/issues/185)
- Internal SA POC kickoff. Deploying an instance of Galaxy for internal use. Only visible changes will be the addition of deployment playbooks and roles for creating the new environment. [#192](https://github.com/ansible/galaxy/issues/192)

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


