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

    var namespaceApp = angular.module('namespaceApp', [
        'ngResource',
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'ui.select',
        'currentUserService',
        'userService',
        'paginateService',
        'namespaceService',
        'namespaceController',
        'namespaceAddController',
        'providerSourceService'
    ]);

    namespaceApp.config(['$routeProvider', '$logProvider', '$resourceProvider', 'uiSelectConfig', _config]);
    namespaceApp.run(['$rootScope', '$location', _run]);

    function _config($routeProvider, $logProvider, $resourceProvider, uiSelectConfig) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        uiSelectConfig.theme = 'bootstrap';
        $logProvider.debugEnabled(debug);
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $routeProvider.
            when('/namespaces/add', {
                templateUrl: '/static/partials/my-namespaces-add.html',
                controller: 'NamespaceAddCtrl'
            }).
            when('/namespaces/:namespace_id', {
                templateUrl: '/static/partials/blank-page.html',
                controller: 'RedirectToDetail'
            }).
            when('/namespaces', {
                templateUrl: '/static/partials/my-namespaces.html',
                controller: 'NamespaceCtrl',
                reloadOnSearch: false,
                resolve: {
                    namespaces: ['namespaceService', 'currentUserService', _getNamespaces]
                }
            }).
            otherwise({
                redirectTo: '/namespaces'
            });
    }

    function _run($rootScope, $location) {
        $rootScope.$on('$routeChangeSuccess', _routeChange);

        function _routeChange() {
            if ($location.path() === '/namespaces') {
                $('#nav-menu-browse-roles').addClass('active');
                $('#nav-menu-browse-users').removeClass('active');
            }
            else {
                $('#nav-menu-browse-roles').removeClass('active');
                $('#nav-menu-browse-users').addClass('active');
            }
        }
    }

    function _getNamespaces(namespaceService, currentUserService) {
        return namespaceService.get({owners: currentUserService.id}).$promise.then(function(response) {
            return response.results;
        });
    }

})(angular);
