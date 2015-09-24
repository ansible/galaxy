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
        'menuController',
        'paginateService',
        'searchService',
        'platformService',
        'commonDirectives',
        'galaxyUtilities',
    ]);

    roleApp.config(['$routeProvider', '$logProvider', _config]);
    roleApp.run(['$rootScope', '$location', _run]);

    function _config($routeProvider, $logProvider) {
        $logProvider.debugEnabled(true);
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

    function _run($rootScope, $location) {
        $rootScope.$on('$routeChangeSuccess', _routeChange);
        
        function _routeChange() {
            if ($location.path() === '/roles') {
                $('#nav-menu-browse-roles').addClass('active');
                $('#nav-menu-browse-users').removeClass('active');
            }
            else {
                $('#nav-menu-browse-roles').removeClass('active');
                $('#nav-menu-browse-users').addClass('active');    
            }
        }
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

})(angular);
