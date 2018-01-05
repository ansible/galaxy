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

    var mod = angular.module('namespaceAddController', ['ngResource']);

    mod.controller('NamespaceAddCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        '$resource',
        '$window',
        '$q',
        '$log',
        'userService',
        'Empty',
        'currentUserService',
        'namespaceService',
        'providerSourceService',
        _NamespaceAddCtrl
    ]);

    function _NamespaceAddCtrl(
        $scope,
        $routeParams,
        $location,
        $timeout,
        $resource,
        $window,
        $q,
        $log,
        userService,
        Empty,
        currentUserService,
        namespaceService,
        providerSourceService
        ) {

        let namespace  = {
            name: '',
            description: '',
            location: '',
            avatar_url: '',
            company: '',
            email: '',
            html_url: '',
            owners: [],
            provider_namespaces: []
        };

        let url_regx = "^(http[s]?:\\/\\/){0,1}(www\\.){0,1}[a-zA-Z0-9\\.\\-]+\\.[a-zA-Z]{2,5}[\\.]{0,1}$"

        $scope.page_title = 'My Namespaces';
        $scope.version = GLOBAL_VERSION;
        $scope.github_auth = true;
        $scope.namespace = namespace;
        $scope.url_regx = url_regx;
        $scope.galaxy_users = [];
        $scope.provider_namespaces = [];
        $scope.fetching = true;
        $scope.apiError = {};

        /* methods */
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

        if (!(currentUserService.authenticated && currentUserService.connected_to_github)) {
            $scope.github_auth = false;
            return;
        }

        return;


        function _lookupUsers(search) {
            return userService.query({'username__icontains': search, page_size: 50, order_by: 'username'}).$promise.then(function(response) {
                let results = [];
                response.results.forEach(function(item) {
                    let user = {
                        id: item.id,
                        username: item.username,
                        github_user: item.github_user
                    };
                    results.push(user);
                });
                $scope.galaxy_users = results;
            });
        }

        function _emptyExists(list) {
            let empty_exists = false;
            namespace[list].forEach(function(item) {
                if (!item) {
                    empty_exists = true;
                }
            });
            return empty_exists;
        }

        function _addOwner() {
            if (!_emptyExists('owners')) {
                namespace.owners.push('');
            }
        }

        function _removeOwner(index) {
            if (index > -1) {
                namespace.owners.splice(index, 1);
                _clearError('owners', index);
            }
        }

        function _addNamespace() {
            if (!_emptyExists('provider_namespaces')) {
                namespace.provider_namespaces.push('');
            }
        }

        function _removeNamespace(index) {
            if (index > -1) {
                namespace.provider_namespaces.splice(index, 1);
                _clearError('provider_namespaces', index);
            }
        }

        function _lookupNamespaces() {
            return providerSourceService.query().$promise.then(function(response) {
                response.forEach(function(item) {
                    $scope.provider_namespaces = response;
                });
            });
        }

        function _saveNamespace(form) {
            let deferred = $q.defer();
            $timeout(function() {
                // run $apply() to refresh the page after modifying the arrays
                _removeEmptyValues('owners');
                _removeEmptyValues('provider_namespaces');
                deferred.resolve();
            }, 500, true);

            deferred.promise.then(function() {
                namespaceService.save(namespace,
                    function(response) {
                        $location.path('/namespaces');
                    },
                    _handleErrors
                )
            })
        }

        function _handleErrors(error) {
            console.log(error);
            if ('data' in error) {
                if (error['data']['detail']) {
                    // TODO handle 500 errors
                    return;
                }
                for (var key in error['data']) {
                    if (typeof error['data'][key] == 'string') {
                        $scope.apiError[key] = error['data'][key];
                    }
                    else if (typeof error['data'] == 'object') {
                        $scope.apiError[key] = [];
                        for (var i=0; i < namespace[key].length; i++) {
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
            for (var i=0; i < namespace[list_name].length; i++) {
                if (!namespace[list_name][i]) {
                    missing_keys.push(i);
                }
            }
            missing_keys.forEach(function(item){
                namespace[list_name].splice(item, 1);
            });
        }

        function _validNamespaces() {
            /* Check that one provider namespace has been selected */
            let valid = false;
            if (!namespace.provider_namespaces.length) {
                return valid;
            }
            namespace.provider_namespaces.forEach(function(item) {
                if (item.name) {
                    valid = true;
                }
            });
            return valid
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
    }

})(angular);
