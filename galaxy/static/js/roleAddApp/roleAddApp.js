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
      'ngResource',
      'ngAnimate',
      'ui.bootstrap',
      'galaxyUtilities',
      'roleAddController',
      'githubRepoService',
      'currentUserService',
      'toggle-switch',
      'importService',
      'roleRemoveSerivice',
      'notificationSecretService'
    ]);

    accountsApp.config(['$routeProvider','$logProvider', '$resourceProvider', _config]);

    function _config($routeProvider, $logProvider, $resourceProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $logProvider.debugEnabled(debug);
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $routeProvider.
            when('/', {
                templateUrl: '/static/partials/role-add.html',
                controller: 'RoleAddCtrl',
                resolve: {
                    repositories: ['githubRepoService', 'currentUserService', _getRepositories]
                }
            }).
            otherwise({
                redirectTo: '/'
            });
    }

    function _getRepositories(githubRepoService) {
        return githubRepoService.get().$promise.then(function(response) {
            return response.results;
        });
    }

})(angular);
