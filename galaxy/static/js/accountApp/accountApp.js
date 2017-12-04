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

    var accountsApp = angular.module('accountsApp', [
      'ngRoute',
      'ngSanitize',
      'ngCookies',
      'ui.bootstrap',
      'meService',
      'storageService',
      'relatedService',
      'myRolesController',
      'galaxyUtilities'
    ]);

    accountsApp.config(['$routeProvider','MyInfoProvider', '$logProvider', _config]);

    function _config($routeProvider, MyInfoProvider, $logProvider) {
        var debug = (GLOBAL_DEBUG === 'on') ? true : false;
        $logProvider.debugEnabled(debug);
        $routeProvider.
            when('/', {
                templateUrl: '/static/partials/myroles.html',
                controller: 'MyRolesCtrl',
                resolve: {
                    my_info: ['$q', 'meFactory', MyInfoProvider.$get[2]]
                }
            }).
            otherwise({
                redirectTo: '/'
            });
    }

})(angular);
