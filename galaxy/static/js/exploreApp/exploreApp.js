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
        'ui.bootstrap',
        'exploreController',
        'tagService',
        'roleSearchService',
        'userService',
        'angulartics', 
        'angulartics.google.analytics'
    ]);

    mod.config(['$routeProvider', '$logProvider', '$resourceProvider', _config]);

    function _config($routeProvider, $logProvider, $resourceProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $resourceProvider.defaults.stripTrailingSlashes = false;
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
