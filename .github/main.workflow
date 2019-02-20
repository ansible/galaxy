workflow "Code linting" {
  on = "push"
  resolves = ["Flake8"]
}

action "Flake8" {
  uses = "cclauss/GitHub-Action-for-Flake8@0.0.1"
  args = "flake8 galaxy/"
}
