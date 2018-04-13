#!/usr/bin/env bash

# Smoke test for ansible-galaxy client and galaxy server.
# NOTE: does zero validation or assertions at the moment, it just
#       scripts running most of the commands. It always exists 0.
#       Use with bash -e for fail on error atm

cleanup() {

    rm -fr ~/.ansible/content/*
}

display() {
    printf "##### TEST: %s\n" "${@}"
}

TEST_NEW=1
GITHUB_USER="${GITHUB_USER:-alikins}"
GITHUB_SMOKE_REPO="${GITHUB_SMOKE_REPO:-ansible-role-galaxy-smoke}"
GALAXY_URL="http://localhost:8000"
VERBOSITY="-vvvvv"
ARGS="${VERBOSITY} -s ${GALAXY_URL}"

echo "ghu ${GITHUB_USER}"
echo "gmr %{GITHUB_SMOKE_REPO}"

cleanup
ansible-galaxy ${ARGS} --help


cleanup

display "search against hosted"

ansible-galaxy search ${ARGS} nginx
cleanup


ansible-galaxy search ${ARGS}




display "info some role"
ansible-galaxy info ${ARGS} alikins.alikins_test1


display "install alikins.alikins_test1"
ansible-galaxy install ${ARGS} alikins.alikins_test1
cleanup


display "import ${GITHUB_USER} ${GITHUB_SMOKE_REPO}"
ansible-galaxy import ${ARGS} --role-name "galaxy-smoke" "${GITHUB_USER}" "${GITHUB_SMOKE_REPO}"
cleanup

display "install ${GITHUB_USER}.galaxy-smoke"
ansible-galaxy install ${ARGS} "${GITHUB_USER}.galaxy-smoke"
cleanup

ansible-galaxy info ${ARGS} "${GITHUB_USER}.galaxy-smoke"
cleanup

ansible-galaxy search ${ARGS} galaxy-smoke
cleanup


display "delete ${GITHUB_USER} ${GITHUB_SMOKE_REPO}"
ansible-galaxy delete ${ARGS} "${GITHUB_USER}" "${GITHUB_SMOKE_REPO}"
cleanup

display "delete ${GITHUB_USER} galaxy-smoke"
ansible-galaxy delete ${ARGS} "${GITHUB_USER}" "galaxy-smoke"
cleanup

# stop here if we are only testing old ansible-galaxy
if [ ! -n "${TEST_NEW}" ] ; then
    exit 1
fi


display "legacy role from git+https"
ansible-galaxy content-install ${ARGS} git+https://github.com/geerlingguy/ansible-role-ansible.git
cleanup


display "legacy role from galaxy"
ansible-galaxy content-install ${ARGS} geerlingguy.ansible
cleanup


display "legacy role from galaxy with dependencies"
ansible-galaxy content-install ${ARGS} hxpro.nginx
cleanup


display "modules from git+https WITHOUT galaxyfile"
ansible-galaxy content-install -t module git+https://github.com/maxamillion/test-galaxy-content $verbosity
cleanup


display "module_utils from git+https WITHOUT galaxyfile"
ansible-galaxy content-install -t module_util git+https://github.com/maxamillion/test-galaxy-content $verbosity
cleanup


display "all content git+https WITH galaxyfile"
ansible-galaxy content-install git+https://github.com/maxamillion/test-galaxy-content-galaxyfile $verbosity
cleanup
