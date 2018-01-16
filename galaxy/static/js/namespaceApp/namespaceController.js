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

    var mod = angular.module('namespaceController', []);

    mod.controller('NamespaceCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        '$resource',
        '$window',
        '$log',
        '$uibModal',
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
        $uibModal,
        Empty,
        currentUserService,
        namespaceService,
        namespaces) {

        $scope.namespaces = namespaces
        $scope.page_title = 'My Namespaces';
        $scope.version = GLOBAL_VERSION;
        $scope.github_auth = true;
        $scope.openWarning = _openWarning;
        $scope.toggleNamespace = _toggleNamespace;
        $scope.toggleSortReverse = _toggleSortReverse;
        $scope.refresh = _refresh
        $scope.reset = _reset
        $scope.selectSort = _selectSort;

        $scope.sort = {
            selected: {name: 'name', label: 'Name'},
            reverse: false,
            options: [{name: 'name', label: 'Name'},{name:'description', label: 'Description'}, {name: 'modified', label: 'Last Modified'}]
        }

        $scope.refreshing = false;

        $scope.search = {text: ''};

        if (!(currentUserService.authenticated && currentUserService.connected_to_github)) {
            $scope.github_auth = false;
        }

        function _selectSort(item) {
            $scope.sort.selected = item;
        }

        function _toggleSortReverse() {
            $scope.sort.reverse = !$scope.sort.reverse;
        }

        function _reset() {
            $scope.sort.selected = {name: 'name', label: 'Name'};
            $scope.sort.reverse = false;
            $scope.search.text = '';
        }

        function _namespaceRefresh() {
            namespaceService.get({owners: currentUserService.id}).$promise.then(function(response) {
                $scope.namespaces = response.results;
            });
        }

        function _refresh() {
            $scope.refreshing = true;
            namespaceService.query({owners: currentUserService.id, page_size: 100}).$promise.then(
                function(response) {
                    $scope.refreshing = false;
                    $scope.namespaces = response.results;
                }
            );
        }

        function _updateNamespace(obj) {
            namespaceService.update(obj).$promise.then(
                function(response) {},
                function(error) {
                    console.log(error);
                }
            );
        }

        function _toggleNamespace(obj) {
             if (!obj.active) {
                 // user deactivated the namespaces
                 let modalInstance = _openWarning();
                 modalInstance.result.then(function(result) {
                     if (result) {
                         // user clicked OK
                         _updateNamespace(obj);
                     } else {
                         obj.active = !obj.active;
                     }
                 });
             } else {
                _updateNamespace(obj);
             }
        }

        function _openWarning(size, parentSelector) {
            let modalInstance = $uibModal.open({
                animation: true,
                ariaLabelledBy: 'modal-title',
                ariaDescribedBy: 'modal-body',
                backdrop: true,
                templateUrl: '/static/partials/modal-continue.html',
                controller: 'namespaceAlertCtrl',
                size: 'lg',
                resolve: {}
            });

            return modalInstance;
        }
    }

    mod.controller('namespaceAlertCtrl', ['$scope', '$uibModalInstance', _namespaceAlertCtrl]);

    function _namespaceAlertCtrl($scope, $uibModalInstance) {
        $scope.$modal = {
            ok: _ok,
            cancel: _cancel,
            title: 'Warning!',
            text: '<p>This will deactivate the Namespace along with any associated content. The content ' +
                  'will <i>NOT</i> be accessible, which means it cannot be downloaded, until it is once again ' +
                  'associated with an active Namespace.</p><p>Do you want to continue?</p>'
        }

        function _ok() {
            $uibModalInstance.close(true);
        }

        function _cancel() {
            $uibModalInstance.close(false);
        }
    }



})(angular);
