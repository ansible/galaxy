/*
 * listApp.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
  
    var roleApp = angular.module('detailApp', [
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
        'roleDetailController',
        'userDetailController',
        'menuController',
        'paginateService',
        'searchService',
        'platformService',
        'commonDirectives',
        'galaxyUtilities'
    ]);

    roleApp.config(['$routeProvider', '$logProvider', _config]);
    roleApp.run(['$rootScope', '$location', _run]);

    function _config($routeProvider, $logProvider) {
      $logProvider.debugEnabled(false);
      $routeProvider.
          when('/role/:role_id', {
              templateUrl: '/static/partials/role-detail.html',
              controller: 'RoleDetailCtrl',
              resolve: {
                  role: ['roleFactory', '$route', _getRole],
                  my_info: ['$q', 'meFactory', _getMyInfo]
              }
          }).
          when('/user/:user_id', {
              templateUrl: '/static/partials/user-detail.html',
              controller: 'UserDetailCtrl',
              resolve: {
                  user: ['userFactory', '$route', _getUser],
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
            if (/\/role/.test($location.path())) {
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

    function _getRole(roleFactory, $route) {
        return roleFactory.getRole($route.current.params.role_id).then(function(data) { return data.data; });
    }

    function _getUser(userFactory, $route) {
        return userFactory.getUser($route.current.params.user_id).then(function(data) { return data.data; });
    }

})(angular);
