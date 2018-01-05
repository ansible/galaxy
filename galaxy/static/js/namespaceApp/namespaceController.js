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

    var mod = angular.module('namespaceController', ['ngResource']);

    mod.controller('NamespaceCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        '$resource',
        '$window',
        '$log',
        'Empty',
        'currentUserService',
        'namespaceService',
        'namespaces',
        _NamespaceCtrl
    ]);

    function _NamespaceCtrl(
        $scope,
        $routeParams,
        $location,
        $timeout,
        $resource,
        $window,
        $log,
        Empty,
        currentUserService,
        namespaceService,
        namespaces) {


        $scope.namespaces = namespaces
        $scope.page_title = 'My Namespaces';
        $scope.version = GLOBAL_VERSION;
        $scope.github_auth = true;
        $scope.namespaceDelete = _namespaceDelete;

        if (!(currentUserService.authenticated && currentUserService.connected_to_github)) {
            $scope.github_auth = false;
            return;
        }

        return;

        function _namespaceRefresh() {
            namespaceService.get({owners: currentUserService.id}).$promise.then(function(response) {
                $scope.namespaces = response.results;
            });
        }

        function _namespaceDelete(obj) {
             console.log(obj);
             namespaceService.delete({}, {id: obj.id}).$promise.then(
                function(response) {
                    _namespaceRefresh();
                },
                function(error) {
                    // TODO add dialog to show an 500 errors
                    console.log(error);
                }
             )
        }
    }

})(angular);
