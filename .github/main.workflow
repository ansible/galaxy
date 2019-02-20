workflow "Code linting" {
  on = "push"
  resolves = [
    "Flake8",
    "ansible/ansible-lint/.github/action@master",
  ]
}

action "Flake8" {
  uses = "cclauss/GitHub-Action-for-Flake8@0.0.1"
  args = "flake8 galaxy/"
}

action "ansible/ansible-lint/.github/action@master" {
  uses = "ansible/ansible-lint/.github/action@master"
  env = {
    ACTION_PLAYBOOK_NAME = "testing/simple/test.yml"
  }
}
