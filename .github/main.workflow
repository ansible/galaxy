workflow "Code linting" {
  on = "push"
  resolves = [
    "Flake8",
    "Ansible Lint",
  ]
}

action "Flake8" {
  uses = "cclauss/GitHub-Action-for-Flake8@0.0.1"
  args = "flake8 galaxy/"
}

action "Ansible Lint" {
  uses = "ansible/ansible-lint/.github/action@master"
  env = {
    ACTION_PLAYBOOK_NAME = "testing/simple/test.yml"
  }
}
