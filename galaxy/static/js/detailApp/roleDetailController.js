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
        '$q',
        '$scope',
        '$routeParams',
        '$location',
        '$modal',
        '$compile',
        'roleFactory',
        'userFactory',
        'relatedFactory',
        'my_info',
        'Stars',
        'PaginateInit',
        'queryParams',
        'fromQueryParams',
        'role',
        'headerService',
        _roleDetailCtrl
    ]);

    function _roleDetailCtrl(
        $q,
        $scope,
        $routeParams,
        $location,
        $modal,
        $compile,
        roleFactory,
        userFactory,
        relatedFactory,
        my_info,
        Stars,
        PaginateInit,
        queryParams,
        fromQueryParams,
        role,
        headerService) {

        $scope.page_title = 'Role Detail';
        $scope.showRoleName = false;
        $scope.my_info = my_info;

        $scope.list_data = {
            'ratings' : {
                'list_filter'        : '',
                'num_pages'          : 1,
                'page'               : 1,
                'page_size'          : 10,
                'reverse'            : false,
                'selected_categories': [],
                'sort_order'         : '-created',
                'refresh'            : null
            }
        };

        headerService.setTitle('Galaxy - ' + role.namespace + '.' + role.name);  // update the page title element

        $scope.role = role;
        $scope.ratings = [];
        $scope.display_user_info = 1;
        $scope.getRole = _getRole;
        $scope.staffDeleteRole = _deleteRole;
        PaginateInit({'scope': $scope});

        return; 

        function _deleteRole(id) {
            roleFactory.deleteRole(id)
                .success(function (data) {
                    $location.path('/roles');
                })
                .error(function (error) {
                    alert("Failed to remove role "+id+", reason: "+error);
                });
        }

        function _getRole() {
            $scope.loading = 1;
            roleFactory.getRole($routeParams.role_id)
                .success( function(data) {
                    $scope.role = data;
                    $scope.loading = 0;
                    _refreshRatings();
                })
                .error( function(error) {
                    $scope.status = 'Unable to load role: ' + error.message;
                });
        }

        function _getRelated(target, url) {
            $scope.list_data[target].url = url;
            $scope.loading = 1;
            relatedFactory.getRelated($scope.list_data[target])
                .success( function(data) {
                    $scope.list_data[target].page = parseInt(data['cur_page']);
                    $scope.list_data[target].num_pages = parseInt(data['num_pages']);
                    $scope.list_data[target].count = parseInt(data['count']);
                    $scope.list_data[target].page_range = [];
                    $scope.setPageRange(target);
                    $scope[target] = data['results'];
                    $scope.loading = 0;
                })
                .error(function (error) {
                    $scope.status = 'Unable to load related '+target+': ' + error.message;
                });
        }
    }

})(angular);