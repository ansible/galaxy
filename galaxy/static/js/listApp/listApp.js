/*
 * listApp.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
  
    var roleApp = angular.module('listApp', [
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'meService',
        'tagService',
        'ratingService',
        'roleService',
        'roleSearchService',
        'storageService',
        'userService',
        'relatedService',
        'roleListController',
        'userListController',
        'paginateService',
        'searchService',
        'platformService',
        'commonDirectives',
        'galaxyUtilities',
        'dc.endlessScroll'
    ]);

    roleApp.config(['$routeProvider', _routes]);

    function _routes($routeProvider) {
        $routeProvider.
            when('/roles', {
                templateUrl: '/static/partials/role-list.html',
                controller: 'RoleListCtrl',
                reloadOnSearch: false,
                resolve: {
                    my_info: ['$q', 'meFactory', _getMyInfo]
                }
            }).
            when('/users', {
                templateUrl: '/static/partials/user-list.html',
                controller: 'UserListCtrl',
                reloadOnSearch: false,
                resolve: {
                    my_info: ['$q', 'meFactory', _getMyInfo]
                }
            }).
            otherwise({
                redirectTo: '/roles'
            });
    }

    function _getMyInfo($q, meFactory) {
        var d = $q.defer();
        meFactory.fetchMyInfo()
            .success(function(data) {
                meFactory.saveInfo(data);
                d.resolve(data);
                })
            .error(function(err) {
                d.reject(err);
                });
        return d.promise;
    }

    function _getRole(roleFactory, $route) {
        return roleFactory.getRole($route.current.params.role_id).then(function(data) { return data.data; });
    }

})(angular);
