/*
 * roleAddController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
    
    var mod = angular.module('roleAddController', []);

    mod.controller('RoleAddCtrl', [
        '$scope',
        '$interval',
        '$timeout',
        'githubRepoService',
        'currentUserService',
        'importService',
        'roleRemoveService',
        'repositories',
        'notificationSecretService',
        _controller
    ]);

    function _controller(
        $scope,
        $interval,
        $timeout,
        githubRepoService,
        currentUserService,
        importService,
        roleRemoveService,
        repositories,
        notificationSecretService) {

        $scope.repositories = repositories;
        $scope.username = currentUserService.username;
        $scope.toggleRepository = _toggleRepository;
        $scope.refreshing = false;
        $scope.refreshRepos = _refresh;
        $scope.showIntegrations = _showIntegrations;
        $scope.cancelIntegrations = _cancelIntegrations;
        $scope.revealGithub = _revealGithub;
        $scope.revealTravis = _revealTravis;
        $scope.clearTravis = _clearTravis;
        $scope.clearGithub = _clearGithub;
        $scope.updateSecrets = _updateSecrets;
        
        _setup();
        
        return;

        function _setup() {
            $scope.repositories.forEach(function(repo) {
                repo.github_secret_type = "password";
                repo.travis_token_type = "password";
                if (repo.summary_fields) {
                    repo.summary_fields.notification_secrets.forEach(function(secret) {
                        if (secret.source == 'travis') {
                            repo.travis_id = secret.id;
                            repo.travis_token = secret.secret;
                        } else {
                            repo.github_id = secret.id;
                            repo.github_secret = secret.secret;
                        }
                    });
                }
                console.log(repo);
            });
        }

        function _showIntegrations(_repo) {
            _repo.show_integrations = !_repo.show_integrations; 
            _repo.github_secret_type = "password";
            _repo.travis_token_type = "password";
            if (_repo.show_integrations) {
                // reveal the form. keep a copy in case user clicks cancel.
                console.log('set master');
                $scope.master = {
                    travis_id: _repo.travis_id,
                    travis_token: _repo.travis_token,
                    github_id: _repo.github_id,
                    github_secret: _repo.github_secret
                };
            }
        }

        function _cancelIntegrations(_repo) {
            _repo.travis_id = $scope.master.travis_id;
            _repo.travis_token = $scope.master.travis_token;
            _repo.github_id = $scope.master.github_id;
            _repo.github_secret = $scope.github_secret;
            _repo.show_integrations = !_repo.show_integrations; 
        }

        function _revealGithub(_repo) {
            _repo.github_secret_type = (_repo.github_secret_type == 'password') ? 'text' : 'password';
        }

        function _revealTravis(_repo) {
            _repo.travis_token_type = (_repo.travis_token_type == 'password') ? 'text' : 'password';
        }

        function _clearTravis(_repo) {
            _repo.travis_token = null;
        }

        function _clearGithub(_repo) {
            _repo.github_secret = null;
        }

        function _updateSecrets(_repo) {
            // deleted secretn
            if (_repo.travis_id && !_repo.travis_token) {
                notificationSecretService.delete({id: _repo.travis_id}).$promise.then(function(repsonse) {
                    _repo.travis_id = null;
                    _repo.show_integrations = false;
                    $timeout(function() {
                        $scope.$apply();
                    },300);
                });
            }
            /*if (_repo.github_id && !_repo.github_secret) {
                _repo.github_id = null;
                notificationSecretService.delete({id: _repo.github_id});
            }*/
            // modified secret
            if (_repo.travis_id && _repo.travis_token && !/^\*{6}/.test(_repo.travis_token)) {
                notificationSecretService.put({
                    id: _repo.travis_id,
                    source: 'travis',
                    github_user: _repo.github_user,
                    github_repo: _repo.github_repo,
                    secret: _repo.travis_token
                }).$promise.then(function(response) {
                    _repo.travis_token = response.secret;
                    _repo.show_integrations = false;
                    $timeout(function() {
                        $scope.$apply();
                    },300);
                });
            }
            // new secret
            if (!_repo.travis_id && _repo.travis_token && !/^\*{6}/.test(_repo.travis_token)) {
                notificationSecretService.save({
                    source: 'travis',
                    github_user: _repo.github_user,
                    github_repo: _repo.github_repo,
                    secret: _repo.travis_token
                }).$promise.then(function(response) {
                    _repo.travis_id = response.id;
                    _repo.travis_token = response.secret;
                    _repo.show_integrations = false;
                    $timeout(function() {
                        $scope.$apply();
                    },300);
                });
            }
        }
        
        function _refresh() {
            $scope.refreshing = true;
            githubRepoService.refresh().$promise.then(function(response) {
                $scope.repositories = response.results;
                _setup();
                $scope.refreshing = false;
                $timeout(function() {
                    $scope.$apply();
                },300);
            });
        }

        function _toggleRepository(_repo) {
            if (_repo.is_enabled) {
                _repo.state = 'PENDING';
                importService.imports.save({
                    'github_user': _repo.github_user,
                    'github_repo': _repo.github_repo,
                }).$promise.then(_checkStatus);
            } else {
                _repo.state = 'PENDING';
                roleRemoveService.delete({
                    'github_user': _repo.github_user,
                    'github_repo': _repo.github_repo
                }).$promise.then(function(response) {
                    $scope.repositories.forEach(function(repo) {
                        response.deleted_roles.forEach(function(deleted) {
                            if (deleted.github_user === repo.github_user && deleted.github_repo === _repo.github_repo) {
                                repo.state = null;
                            }
                        });
                    });
                });
            }
        }

        function _checkStatus(response) {
            var stop = $interval(function(_id) {
                importService.imports.query({ id: _id}).$promise.then(function(response) {
                    $scope.repositories.every(function(repo) {
                        if (repo.github_user == response.results[0].github_user && 
                            repo.github_repo === response.results[0].github_repo) {
                            repo.state = response.results[0].state;
                            return false;
                        }
                        return true;
                    });
                    if (response.results[0].state == 'SUCCESS' || response.results[0].state == 'FAILED') {
                        _kill();
                    }
                });
            }, 5000, 0, false, response.results[0].id)

            function _kill() {
                $interval.cancel(stop);
            }
        }
    }

})(angular);
 

