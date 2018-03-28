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

    var mod = angular.module('namespaceFormService', []);

    mod.factory('namespaceFormService', ['$q', '$timeout', '$location', 'userService', 'namespaceService', 'providerSourceService', 'currentUserService',
        _factory]);

    function _factory(
        $q,
        $timeout,
        $location,
        userService,
        namespaceService,
        providerSourceService,
        currentUserService
        ) {
        return function($scope, operation){

            $scope.version = GLOBAL_VERSION;
            $scope.github_auth = true;
            $scope.fetching = true;
            $scope.apiError = {};
            $scope.alert = {'show': false, 'msg': ''};
            $scope.selected = {owner: null, provider_namespace: null};
            $scope.user_id = currentUserService.id;
            $scope.forms = {};

            $scope.provider_namespaces = [];
            $scope.galaxy_users = [];

            if (!(currentUserService.authenticated && currentUserService.connected_to_github)) {
                $scope.github_auth = false;
            }

            $scope.addOwner = _addOwner;
            $scope.removeOwner = _removeOwner;
            $scope.lookupUsers = _lookupUsers;
            $scope.addNamespace = _addNamespace;
            $scope.removeNamespace = _removeNamespace;
            $scope.lookupNamespaces = _lookupNamespaces;
            $scope.saveNamespace = _saveNamespace;
            $scope.validNamespaces = _validNamespaces;
            $scope.clearError = _clearError;
            $scope.hasApiErrors = _hasApiErrors;
            $scope.fieldHasApiError = _fieldHasApiError;

            function _lookupUsers(search) {
                return userService.query({'username__icontains': search, page_size: 50, order_by: 'username'}).$promise.then(function(response) {
                    let results = [];
                    response.results.forEach(function(item) {
                        if (!_ownerExists(item)) {
                            let user = {
                                id: item.id,
                                username: item.username,
                                github_user: item.github_user,
                                github_avatar: item.github_avatar
                            };
                            results.push(user);
                        }
                    });
                    $scope.galaxy_users = results;
                });
            }

            function _emptyExists(list) {
                let empty_exists = false;
                $scope.namespace[list].forEach(function(item) {
                    if (!item) {
                        empty_exists = true;
                    }
                });
                return empty_exists;
            }

            function _ownerExists(owner) {
                let found = false;
                $scope.namespace.owners.forEach(function(existing) {
                    if (existing.id == owner.id) {
                        found = true;
                    }
                });
                return found;
            }

            function _addOwner() {
                if ($scope.selected.owner && !_ownerExists($scope.selected.owner)) {
                    $scope.namespace.owners.push($scope.selected.owner);
                    $scope.selected.owner = null;
                }
            }

            function _removeOwner(index) {
                if (index > -1) {
                    $scope.namespace.owners.splice(index, 1);
                    _clearError('owners', index);
                    $scope.forms.nsAddForm.$setDirty();
                }
            }

            function _addNamespace() {
                if ($scope.selected.provider_namespace && !_providerExists($scope.selected.provider_namespace)) {
                    $scope.namespace.provider_namespaces.push($scope.selected.provider_namespace);
                    $scope.selected.provider_namespace = null;
                }
            }

            function _removeNamespace(index) {
                if (index > -1) {
                    $scope.namespace.provider_namespaces.splice(index, 1);
                    _clearError('provider_namespaces', index);
                    $scope.forms.nsAddForm.$setDirty();
                }
            }

            function _providerExists(provider) {
                let found = false;
                $scope.namespace.provider_namespaces.forEach(function(existing) {
                    if (existing.name == provider.name) {
                        found = true;
                    }
                });
                return found;
            }

            function _lookupNamespaces() {
                return providerSourceService.query().$promise.then(function(response) {
                    let results = [];
                    response.forEach(function(item) {
                        if (!_providerExists(item)) {
                            results.push(item);
                        }
                    });
                    $scope.provider_namespaces = results;
                });
            }

            function _saveNamespace() {
                let deferred = $q.defer();
                $scope.apiError = {};
                $scope.alert.show = false;

                $timeout(function() {
                    // run $apply() to refresh the page after modifying the arrays
                    _removeEmptyValues('owners');
                    _removeEmptyValues('provider_namespaces');
                    deferred.resolve();
                }, 500, true);

                deferred.promise.then(function() {
                    if (operation == 'save') {
                        namespaceService.save($scope.namespace,
                            function(response) {
                                $location.path('/namespaces');
                            },
                            _handleErrors
                        )
                    } else if (operation == 'update') {
                        namespaceService.update($scope.namespace,
                            function(response) {
                                $location.path('/namespaces');
                            },
                            _handleErrors
                        )
                    }
                })
            }

            function _handleErrors(error) {
                if ('data' in error) {
                    $scope.alert.show = true;
                    if (error['data']['detail']) {
                        $scope.alert.msg = error['data']['detail'];
                        return;
                    }
                    $scope.alert.msg = 'One or more errors were found. See the message under each value needing your attention.';
                    for (var key in error['data']) {
                        if (typeof error['data'][key] == 'string') {
                            $scope.apiError[key] = error['data'][key];
                        }
                        else if (typeof error['data'] == 'object') {
                            $scope.apiError[key] = [];
                            for (var i=0; i < $scope.namespace[key].length; i++) {
                                if (error['data'][key][i]) {
                                    $scope.apiError[key].push(error['data'][key][i]);
                                } else {
                                    $scope.apiError[key].push('');
                                }
                            }
                        }
                    }
                }
            }

            function _removeEmptyValues(list_name) {
                var missing_keys = [];
                for (var i=0; i < $scope.namespace[list_name].length; i++) {
                    if (!$scope.namespace[list_name][i]) {
                        missing_keys.push(i);
                    }
                }
                missing_keys.forEach(function(item){
                    $scope.namespace[list_name].splice(item, 1);
                });
            }

            function _validNamespaces() {
                return true;
            }

            function _clearError(field, index) {
                if (field != 'owners' && field != 'provider_namespaces') {
                    if ($scope.apiError[field]) {
                        delete $scope.apiError[field];
                    }
                } else {
                    if ($scope.apiError[field] && $scope.apiError[field][index]) {
                        $scope.apiError[field].splice(index, 1);
                        if ($scope.apiError[field].length == 0) {
                            delete $scope.apiError[field];
                        }
                    }
                }
            }

            function _hasApiErrors() {
                let cnt = Object.keys($scope.apiError).length;
                return cnt > 0;
            }

            function _fieldHasApiError(key, index) {
                if (key == 'provider_namespaces' || key == 'owners') {
                    if ($scope.apiError[key] && $scope.apiError[key].length > index && $scope.apiError[key][index]) {
                        return true;
                    }
                } else {
                    if ($scope.apiError[key]) {
                        return true;
                    }
                }
                return false;
            }
        }
    }
})(angular);