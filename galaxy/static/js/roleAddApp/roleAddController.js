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
        'githubRepoService',
        'currentUserService',
        'importService',
        'roleRemoveService',
        'repositories',
        _controller
    ]);

    function _controller(
        $scope,
        $interval,
        githubRepoService,
        currentUserService,
        importService,
        roleRemoveService,
        repositories) {

        $scope.repositories = repositories;
        $scope.username = currentUserService.username;
        $scope.toggleRepository = _toggleRepository;
        $scope.refreshing = false;
        $scope.refreshRepos = _refresh;
        $scope.showIntegrations = _showIntegrations;
        $scope.revealGithub = _revealGithub;
        $scope.revealTravis = _revealTravis;
        $scope.clearTravis = _clearTravis;
        $scope.clearGithub = _clearGithub;
        
        _setup();
        
        return;

        function _setup() {
            $scope.repositories.forEach(function(repo) {
                repo.github_secret_type = "password";
                repo.travis_token_type = "password";
            });
        }

        function _showIntegrations(_repo) {
            _repo.show_integrations = !_repo.show_integrations; 
            _repo.github_secret_type = "password";
            _repo.travis_token_type = "password";
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
        
        function _refresh() {
            $scope.refreshing = true;
            githubRepoService.refresh().$promise.then(function(response) {
                $scope.repositories = response.results;
                _setup();
                $scope.refreshing = false;
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
                console.log('looking for id: ' + _id);
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
 

