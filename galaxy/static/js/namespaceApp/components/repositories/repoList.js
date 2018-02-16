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

(function (angular) {

    angular.module('repoComponents').component('repoList', {
        templateUrl: '/static/js/namespaceApp/components/repositories/repoList.html',
        bindings: {
            namespace: '<',
            repoFilter: '<'
        },
        controller: function RepoListController($rootScope, $q, githubRepoService) {
            var $ctrl = this;

            $ctrl.$onInit = function () {
                $ctrl.providerNamespaces = [];
                _loadRepos();
            };

            $rootScope.$on('namespace.update', function(event, namespace) {
                if (namespace.id === $ctrl.namespace.id) {
                    _loadRepos();
                }
            });

            function _loadRepos() {
                var promises = [];
                if (!$ctrl.repositories || $ctrl.repositories.length === 0) {
                    $ctrl.isLoading = true;
                    $ctrl.isEmpty = false;
                }

                angular.forEach($ctrl.namespace.summary_fields.provider_namespaces, function (pns) {
                    promises.push(githubRepoService.get({ provider_namespace: pns.id }).$promise);
                });

                $q.all(promises).then(function (data) {
                    $ctrl.repositories = [];
                    angular.forEach(data, function (response) {
                        $ctrl.repositories = $ctrl.repositories.concat(response.results);
                    });
                    $ctrl.isLoading = false;
                    $ctrl.isEmpty = $ctrl.repositories.length === 0;
                });
            }
        }
    });

})(angular);
