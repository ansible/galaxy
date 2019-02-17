workflow "Code linting" {
  on = "push"
  resolves = ["GitHub Action for Flake8"]
}

action "GitHub Action for Flake8" {
  uses = "cclauss/GitHub-Action-for-Flake8@0.0.1"
}
