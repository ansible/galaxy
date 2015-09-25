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
        'tagService',
        'roleService',
        'userService',
    ]);

    mod.config(['$routeProvider', '$logProvider', _config]);

    function _config($routeProvider, $logProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $logProvider.debugEnabled(debug);
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
