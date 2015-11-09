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
      'roleAddController'
    ]);

    accountsApp.config(['$routeProvider','MyInfoProvider', '$logProvider', _config]);

    function _config($routeProvider, MyInfoProvider, $logProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $logProvider.debugEnabled(debug);
        $routeProvider.
            when('/', {
                templateUrl: '/static/partials/role-add.html',
                controller: 'RoleAddCtrl'
                //resolve: {
                //    my_info: ['$q', 'meFactory', MyInfoProvider.$get[2]]
                //}
            }).
            otherwise({
                redirectTo: '/'
            });
    }

})(angular);
