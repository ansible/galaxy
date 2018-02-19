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

    angular.module('repoComponents').component('addRepoModal', {
        templateUrl: '/static/js/namespaceApp/components/repositories/addRepoModal.html',
        bindings: {
            resolve: '<',
            close: '&',
            dismiss: '&'
        },
        controller: function ($q, $rootScope, providerSourceService, githubRepoService, importService) {
            var $ctrl = this;

            $ctrl.selectProviderNamespace = _selectProviderNamespace;
            $ctrl.nameFilter = _nameFilter;

            $ctrl.$onInit = function () {
                $ctrl.namespace = $ctrl.resolve.namespace;
                $ctrl.providerNamespaces = [];
                angular.forEach($ctrl.namespace.summary_fields.provider_namespaces, function (pns) {
                    $ctrl.providerNamespaces.push(angular.copy(pns));
                });
                if ($ctrl.providerNamespaces.length > 0) {
                    $ctrl.selectedPNS = $ctrl.providerNamespaces[0]
                }
                _getRepoSources();
            };

            $ctrl.ok = function () {
                _saveSelectedRepos().finally(function() {
                    $rootScope.$emit('namespace.update', $ctrl.namespace);
                });
                $ctrl.close({$value: 'ok'});
            };

            $ctrl.cancel = function () {
                $ctrl.dismiss({$value: 'cancel'});
            };

            function _getRepoSources() {
                angular.forEach($ctrl.providerNamespaces, function (pns) {
                    pns.loading = true;
                    providerSourceService.getRepoSources({
                        providerName: pns.provider_name,
                        name: pns.name
                    }).$promise.then(function (response) {
                        pns.repoSources = [];
                        angular.forEach(response, function(repoSource) {
                            if (!repoSource.summary_fields.repository) {
                                pns.repoSources.push(repoSource);
                            }
                        });
                        pns.loading = false;
                    });
                });
            }

            function _saveSelectedRepos() {
                var saveRepoPromises = [];

                angular.forEach($ctrl.selectedPNS.repoSources, function (repo) {
                    if (repo.selected) {
                        saveRepoPromises.push(_saveAndImportRepo($ctrl.selectedPNS, repo));
                    }
                });

                return $q.all(saveRepoPromises);
            }

            function _saveAndImportRepo(providerNamespace, repoSource) {
                var deferred = $q.defer(); //need to return resolve instead of reject for $q.all

                _saveRepo(providerNamespace, repoSource).then(_importRepo).finally(function() {
                    deferred.resolve();
                });

                return deferred.promise;
            }

            function _saveRepo(providerNamespace, repoSource) {
                var params = {};
                params.name = repoSource.name;
                params.original_name = repoSource.name;
                params.provider_namespace = providerNamespace.id;
                params.is_enabled = true;

                //TODO report error
                return githubRepoService.save(params).$promise
            }

            function _importRepo(repository) {
                //TODO report error
                return importService.imports.save({
                    'github_user': repository.github_user,
                    'github_repo': repository.github_repo,
                    'alternate_role_name': repository.role_name
                }).$promise
            }

            function _selectProviderNamespace(providerNamespace) {
                $ctrl.selectedPNS = providerNamespace;
                $ctrl.nameFilterInput = null;
            }

            function _nameFilter(repository) {
                if (repository.selected == true) {
                    return true;
                }

                if (!$ctrl.nameFilterInput || $ctrl.nameFilterInput === '') {
                    return true;
                }

                return repository.name.toLowerCase().indexOf($ctrl.nameFilterInput.toLowerCase()) >= 0;
            }
        }
    });

})(angular);
