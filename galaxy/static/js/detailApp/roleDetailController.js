/* (c) 2012-2016, Ansible by Red Hat
 *
 * This file is part of Ansible Galaxy
 *
 * Ansible Galaxy is free software: you can redistribute it and/or modify
 * it under the terms of the Apache License as published by
 * the Apache Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Ansible Galaxy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Apache License for more details.
 *
 * You should have received a copy of the Apache License
 * along with Galaxy.  If not, see <http://www.apache.org/licenses/>.
 */

'use list';

(function(angular) {

    var mod = angular.module('roleDetailController', ['headerService']); 

    mod.controller('RoleDetailCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$window',
        'roleService',
        'currentUserService',
        'role',
        'headerService',
        'githubRepoService',
        'userService',
        'githubClickService',
        _roleDetailCtrl
    ]);

    function _roleDetailCtrl(
        $scope,
        $routeParams,
        $location,
        $window,
        roleService,
        currentUserService,
        role,
        headerService,
        githubRepoService,
        userService,
        githubClickService) {

        $scope.page_title = 'Role Detail';
        $scope.showRoleName = false;
        $scope.my_info = currentUserService;
        $scope.loadReadMe = _loadReadMe;
        $scope.readMe = '';
        $scope.is_authenticated = currentUserService.authenticated && currentUserService.connected_to_github;

        headerService.setTitle('Galaxy - ' + role.username + '.' + role.name);  // update the page title element
        $scope.role = role;
        $scope.display_user_info = 1;
        $scope.staffDeleteRole = _deleteRole;

        $scope.subscribe = githubClickService.subscribe;
        $scope.unsubscribe = githubClickService.unsubscribe;
        $scope.star = githubClickService.star;
        $scope.unstar = githubClickService.unstar;
        
        _getUserAvatar();

        return; 


        function _getUserAvatar() {
            userService.get({ "github_user": role.github_user },
                _success, _error);

            function _success(response) {
                if (response.results.length && response.results[0].github_avatar) {
                    $scope.avatar = response.results[0].github_avatar;
                } else {
                    $scope.avatar = "/static/img/avatar.png";
                }
            }

            function _error(response) {
                $scope.avatar = "/static/img/avatar.png";
            }
        }

        function _deleteRole(_role) {
            roleService.delete({ 
                "github_user": _role.github_user,
                "github_repo": _role.github_repo
            }).$promise.then(function(response) {
                $window.location = '/list#/roles';
            });
        }

        function _loadReadMe() {
            if (!$scope.readMe) {
                $scope.loading = true;
                roleService.getReadMe($scope.role.role_id).then(function(readme) {
                    $scope.readMe = readme;
                    $scope.loading = false;
                });
            }
        }

    }

})(angular);
