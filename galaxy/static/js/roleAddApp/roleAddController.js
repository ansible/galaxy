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
        _controller
    ]);

    function _controller($scope, $interval, githubRepoService, currentUserService, importService, roleRemoveService) {

        $scope.repositories = [];
        $scope.username = currentUserService.username;
        $scope.toggleRepository = _toggleRepository;
        
        _getRepositories();

        var longPole = null;

        return;


        function _toggleRepository(_repo) {
            var names = _repo.name.split('/');
            if (_repo.active) {
                _repo.state = 'PENDING';
                importService.imports.save({
                    'github_user': names[0],
                    'github_repo': names[1],
                }).$promise.then(_checkStatus);
            } else {
                _repo.state = 'PENDING';
                roleRemoveService.delete({
                    'github_user': names[0],
                    'github_repo': names[1]
                }).$promise.then(function(response) {
                    $scope.repositories.forEach(function(repo) {
                        var names = repo.name.split('/');
                        response.deleted_roles.forEach(function(deleted) {
                            if (deleted.github_user === names[0] && deleted.github_repo === names[1]) {
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
                        var names = repo.name.split('/');
                        if (names[0] == response.results[0].github_user && 
                            names[1] === response.results[0].github_repo) {
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

        function _getRepositories() {
            $scope.loading = true;
            githubRepoService.get(null, _success, _error);
            
            function _success(data) {
                $scope.repositories = data.results;
                $scope.loading = false;
            }

            function _error(response) {
                console.log(response);
            }
        }
    }

})(angular);
 

