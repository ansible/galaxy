/*
 * exploreApp.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('exploreApp', [
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'exploreController',
        'categoryService',
        'roleService',
        'userService',
    ]);

    mod.config(['$routeProvider', _config]);

    function _config($routeProvider) {
        $routeProvider.
            when('/', {
                templateUrl: '/static/partials/main.html',
                controller: 'ExploreCtrl'
        }).
        otherwise({
            redirectTo: '/'
        });
    }
    
})(angular);
