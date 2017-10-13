# Roadmap

## Release 2.3 (Current Development)

- Cleanup and simplify the development container build and run workflow
- Create a container release workflow that results in pre-baked images hosted on Docker Hub
- Create a simple installer, similar to AWX, that deploys pre-baked Galaxy images to Docker and OpenShift
- Start a framework for backend testing [#37](https://github.com/ansible/galaxy/issues/37)
- Fix [#38](https://github.com/ansible/galaxy/issues/38), 404 page for roles uses 200 status header
- Fix [#47](https://github.com/ansible/galaxy/issues/47), no error when adding a new role/container project that has the same name as an existing project


## Release 2.4 (Future)

- Investigate replacing Galaxy home page with an OpenSource CMS 
- Support adding embedded video to the detail page of a 'role' via meta data
- Make it easy to add custom branding
