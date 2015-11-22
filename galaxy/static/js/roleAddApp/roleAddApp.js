/*
 * roleAddApp.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var accountsApp = angular.module('roleAddApp', [
      'ngRoute',
      'ngSanitize',
      'ngCookies',
      'ui.bootstrap',
      'meService',
      'galaxyUtilities',
      'roleAddController',
      'githubRepoService',
      'currentUserService',
      'toggle-switch',
      'importService',
      'roleRemoveSerivice'
    ]);

    accountsApp.config(['$routeProvider','MyInfoProvider', '$logProvider', '$resourceProvider', _config]);

    function _config($routeProvider, MyInfoProvider, $logProvider, $resourceProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $logProvider.debugEnabled(debug);
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $routeProvider.
            when('/', {
                templateUrl: '/static/partials/role-add.html',
                controller: 'RoleAddCtrl',
            }).
            otherwise({
                redirectTo: '/'
            });
    }

})(angular);
