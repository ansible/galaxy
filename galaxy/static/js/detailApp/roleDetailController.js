/*
 * roleDetailController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use list';

(function(angular) {

    var mod = angular.module('roleDetailController', ['headerService']); 

    mod.controller('RoleDetailCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        'roleService',
        'currentUserService',
        'role',
        'headerService',
        'githubRepoService',
        'userService',
        _roleDetailCtrl
    ]);

    function _roleDetailCtrl(
        $scope,
        $routeParams,
        $location,
        roleService,
        currentUserService,
        role,
        headerService,
        githubRepoService,
        userService) {

        $scope.page_title = 'Role Detail';
        $scope.showRoleName = false;
        $scope.my_info = currentUserService;
        $scope.loadReadMe = _loadReadMe;
        $scope.readMe = '';
        $scope.is_authenticated = currentUserService.authenticated;

        headerService.setTitle('Galaxy - ' + role.username + '.' + role.name);  // update the page title element

        $scope.role = role;
        $scope.display_user_info = 1;
        $scope.staffDeleteRole = _deleteRole;

        $scope.subscribe = function () {
            if (currentUserService.authenticated)
                _subscribe();
        }
        $scope.unsubscribe = function () { 
            if (currentUserService.authenticated)
                _unsubscribe();
        }
        $scope.star = function () { 
            if (currentUserService.authenticated)
                _star();
        }
        $scope.unstar = function () { 
            if (currentUserService.authenticated)
                _unstar();
        }

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

        function _deleteRole(id) {
            roleService.deleteRole(id).$promise.then(function(response) {
                $location.path('/roles');
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

        function _subscribe() {
            // Subscribe the user to the role repo
            role.subscribing = true;
            githubRepoService.subscribe({
                github_user: role.github_user,
                github_repo: role.github_repo
            }).$promise.then(function() {
                role.watchers_count++;
                role.user_is_subscriber = true;
                role.subscribing = false;
                currentUserService.update();
            });
        }

        function _unsubscribe() {
            // Find the user's subscription to the role repo and delete it
            role.subscribing = true;
            var id;
            currentUserService.subscriptions.every(function(sub) {
                if (sub.github_user == role.github_user && sub.github_repo == role.github_repo) {
                    id = sub.id;
                    return false;
                }
                return true;
            });
            if (id) {
                githubRepoService.unsubscribe({
                    id: id
                }).$promise.then(function() {
                    role.watchers_count--;
                    role.user_is_subscriber = false;
                    role.subscribing = false;
                    currentUserService.update();
                });
            } else {
                role.subscribing = false;
            }
        }

        function _star() {
            // Subscribe the user to the role repo
            role.starring = true;
            githubRepoService.star({
                github_user: role.github_user,
                github_repo: role.github_repo
            }).$promise.then(function() {
                role.stargazers_count++;
                role.user_is_stargazer = true;
                role.starring = false;
                currentUserService.update();
            });
        }

        function _unstar() {
            // Find the user's subscription to the role repo and delete it
            role.starring = true;
            var id;
            currentUserService.starred.every(function(star) {
                if (star.github_user == role.github_user && star.github_repo == role.github_repo) {
                    id = star.id;
                    return false;
                }
                return true;
            });
            if (id) {
                githubRepoService.unstar({
                    id: id
                }).$promise.then(function() {
                    role.stargazers_count--;
                    role.user_is_stargazer = false;
                    role.starring = false;
                    currentUserService.update();
                });
            } else {
                role.starring = false;
            }
        }
    }

})(angular);