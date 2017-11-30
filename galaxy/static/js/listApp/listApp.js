/* (c) 2012-2018, Ansible by Red Hat
 *
 * This file is part of Ansible Galaxy
 *
 * Ansible Galaxy is free software: you can redistribute it and/or modify
 * it under the terms of the Apache License as published by
 * the Apache Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Ansible Galaxy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Apache License for more details.
 *
 * You should have received a copy of the Apache License
 * along with Galaxy.  If not, see <http://www.apache.org/licenses/>.
 */

'use strict';

(function(angular) {
  
    var roleApp = angular.module('listApp', [
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'tagService',
        'ratingService',
        'roleSearchService',
        'storageService',
        'userService',
        'relatedService',
        'roleListController',
        'menuController',
        'paginateService',
        'searchService',
        'platformService',
        'commonDirectives',
        'galaxyUtilities',
        'githubRepoService',
        'githubClickService',
        'currentUserService',
        'angulartics', 
        'angulartics.google.analytics'
    ]);

    roleApp.config(['$routeProvider', '$logProvider', '$resourceProvider', _config]);
    roleApp.run(['$rootScope', '$location', _run]);
    roleApp.controller('RedirectToDetail', ['$routeParams', '$window', _redirectToDetail]);

    function _config($routeProvider, $logProvider, $resourceProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $logProvider.debugEnabled(debug);
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $routeProvider.
            when('/roles/:role_id', {
                templateUrl: '/static/partials/blank-page.html',
                controller: 'RedirectToDetail'
            }).
            when('/roles', {
                templateUrl: '/static/partials/role-list.html',
                controller: 'RoleListCtrl',
                reloadOnSearch: false
            }).
            otherwise({
                redirectTo: '/roles'
            });
    }

    function _redirectToDetail($routeParams, $window) {
        // Allow /list#/role/:role_id to still work by redirecting
        // to /detail#/role/:role_id
        $window.location.replace("/detail#/role/" + $routeParams.role_id + "/");
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

})(angular);
