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
        '$timeout',
        '$resource',
        '$window',
        '$log',
        '$location',
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
        $timeout,
        $resource,
        $window,
        $log,
        $location,
        $uibModal,
        Empty,
        currentUserService,
        namespaceService,
        namespaces) {

        $scope.namespaces = namespaces

        $scope.namespaces.forEach(function(item) {
            item.expandField = null;
            item.isExpanded = false;
        });

        $scope.items = namespaces;

        $scope.page_title = 'My Namespaces';
        $scope.version = GLOBAL_VERSION;
        $scope.github_auth = true;
        $scope.openWarning = _openWarning;
        $scope.toggleNamespace = _toggleNamespace;
        $scope.enableButtonForItemFn = _enableButtonForItemFn;
        $scope.updateMenuActionForItemFn = _updateMenuActionForItemFn;
        $scope.addNamespace = _addNamespace
        $scope.refresh = _refresh;


        $scope.customScope = {
            toggleExpandItemField: _toggleExpandItemField,
            collapseItem: _collapseItem,
            isItemExpanded: _isItemExpanded
        };

        $scope.actionButtons = [
            {
                name: 'Add Content',
                title: 'Update namespace content',
                actionFn: _emptyStateAction
            }
        ];

        $scope.menuActions = [
            {
                name: 'Edit Properties',
                title: 'Edit namespace properties',
                actionFn: _editProperties
            },
            {
                name: 'Disable',
                title: 'Disable the namespace and its content',
                actionFn: _toggleNamespace
            },
            {
                name: 'Enable',
                title: 'Enable the namespace and its content',
                actionFn: _toggleNamespace
            }
        ];

        $scope.listConfig = {
            showSelectBox: false,
            itemsAvailable: true,
            useExpandingRows: true,
            compoundExpansionOnly: true
        };

        $scope.toolbarConfig = {
            filterConfig: {
                fields: [{
                    id: 'name',
                    title: 'Name',
                    placeholder: 'Filter by name',
                    filterType: 'text'
                },
                {
                    id: 'description',
                    title: 'Description',
                    placeholder: 'Filter on description',
                    filterType: 'text'
                }],
                appliedFilters: [],
                resultsCount: $scope.items.length,
                totalCount: $scope.namespaces.length,
                onFilterChange: _filterChange
            },
            sortConfig: {
                fields: [{
                    id: 'name',
                    title: 'Name',
                    sortType: 'alpha'
                },
                {
                    id: 'description',
                    title: 'Description',
                    sortType: 'alpha'
                }],
                onSortChange: _sortChange
            },
            actionsConfig: {
                actionsInclude: true
            }
        }

        $scope.refreshing = false;

        if (!(currentUserService.authenticated && currentUserService.connected_to_github)) {
            $scope.github_auth = false;
        }

        function _enableButtonForItemFn(action, item) {
            return item.active;
        };

        function _updateMenuActionForItemFn(action, item) {
            if ((action.name == 'Edit Properties') || (action.name == 'Disable' && item.active) ||
                (action.name == 'Enable' && !item.active)) {
                action.isVisible = true;
            } else {
                action.isVisible = false;
            }
        }

        function _editProperties(action, item) {
            $location.path('/namespaces/' + item.id);
        }

        function _toggleExpandItemField(item, field) {
            if (item.isExpanded && item.expandField === field) {
                item.isExpanded = false;
            } else {
                item.isExpanded = true;
                item.expandField = field;
            }
        }

        function _collapseItem(item) {
            item.isExpanded = false;
        }

        function _isItemExpanded(item, field) {
            return item.isExpanded && item.expandField === field;
        }

        function _emptyStateAction(action, item) {
            console.log(item.name + " : " + action.name);
        }


//        function _namespaceRefresh() {
//            namespaceService.get({owners: currentUserService.id}).$promise.then(function(response) {
//                $scope.namespaces = response.results;
//            });
//        }

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

        function _toggleNamespace(action, item) {
            if (action.name == 'Disable') {
                 let modalInstance = _openWarning();
                 modalInstance.result.then(function(result) {
                     if (result) {
                         // user clicked OK
                         item.active = false;
                         _updateNamespace(item);
                     }
                 });
            } else {
                item.active = true;
                _updateNamespace(item);
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

        function _matchesFilter(item, filter) {
            var match = true;
            var re = new RegExp(filter.value, 'i');

            if (filter.id === 'name') {
                match = item.name.match(re) !== null;
            } else if (filter.id === 'description') {
                match = item.description.match(re) !== null;
            }
           return match;
        };

        function _matchesFilters(item, filters) {
            var matches = true;
            filters.forEach(function(filter) {
                if (!_matchesFilter(item, filter)) {
                    matches = false;
                    return false;
                }
            });
            return matches;
        };

        function _applyFilters(filters) {
            $scope.items = [];
            if (filters && filters.length > 0) {
                $scope.namespaces.forEach(function (item) {
                    if (_matchesFilters(item, filters)) {
                        $scope.items.push(item);
                    }
                });
            } else {
                $scope.items = $scope.namespaces;
            }
            $scope.toolbarConfig.resultsCount = $scope.items.length;
        };

        function _filterChange(filters) {
            $scope.filtersText = "";
            filters.forEach(function (filter) {
                $scope.filtersText += filter.title + " : ";
                if (filter.value.filterCategory) {
                    $scope.filtersText += ((filter.value.filterCategory.title || filter.value.filterCategory)
                        + filter.value.filterDelimiter + (filter.value.filterValue.title || filter.value.filterValue));
                } else if (filter.value.title){
                    $scope.filtersText += filter.value.title;
                } else {
                    $scope.filtersText += filter.value;
                }
                $scope.filtersText += "\n";
            });
            _applyFilters(filters);
        };

        function _compareFn(item1, item2) {
            let compValue = 0;
            let field = $scope.toolbarConfig.sortConfig.currentField.id
            compValue = item1[field].localeCompare(item2[field]);
            if (!$scope.toolbarConfig.sortConfig.isAscending) {
                compValue = compValue * -1;
            }
            return compValue;
        };

        function _sortChange(sortId, isAscending) {
            $scope.items.sort(_compareFn);
        };

        function _addNamespace() {
            $location.path('/namespaces/add');
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
