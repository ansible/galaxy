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
        _roleDetailCtrl
    ]);

    function _roleDetailCtrl(
        $scope,
        $routeParams,
        $location,
        roleService,
        currentUserService,
        role,
        headerService) {

        $scope.page_title = 'Role Detail';
        $scope.showRoleName = false;
        $scope.my_info = currentUserService;

        headerService.setTitle('Galaxy - ' + role.namespace + '.' + role.name);  // update the page title element

        $scope.role = role;
        $scope.display_user_info = 1;
        $scope.staffDeleteRole = _deleteRole;

        return; 

        function _deleteRole(id) {
            roleService.deleteRole(id).$promise.then(function(response) {
                $location.path('/roles');
            });
        }
    }

})(angular);