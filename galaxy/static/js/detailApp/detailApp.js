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
        'ui.bootstrap',
        'currentUserService',
        'roleService',
        'storageService',
        'roleDetailController',
        'headerController',
        'menuController',
        'headerService',
        'commonDirectives',
        'galaxyUtilities',
        'githubRepoService',
        'githubClickService',
        'userService',
        'angulartics', 
        'angulartics.google.analytics'
    ]);

    roleApp.config(['$routeProvider', '$logProvider', '$resourceProvider', _config]);
    roleApp.run(['$rootScope', '$location', _run]);

    function _config($routeProvider, $logProvider, $resourceProvider) {
      var debug = (GLOBAL_DEBUG === 'on') ? true : false;
      $logProvider.debugEnabled(debug);
      // $resourceProvider.defaults.stripTrailingSlashes = false;
      $routeProvider.
          when('/role/:role_id', {
              templateUrl: '/static/partials/role-detail.html',
              controller: 'RoleDetailCtrl',
              resolve: {
                  role: ['roleService', '$route', _getRole]
              }
          }).
          otherwise({
              redirectTo: '/role/999999'
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

    function _getRole(roleService, $route) {
        return roleService.get({ "role_id": $route.current.params.role_id }).$promise.then(function(response) {
            if (response.results.length)
                return response.results[0];
            return [];
        });
    }

})(angular);
