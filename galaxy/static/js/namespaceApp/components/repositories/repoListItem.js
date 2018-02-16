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

    angular.module('repoComponents').component('repoListItem', {
        templateUrl: '/static/js/namespaceApp/components/repositories/repoListItem.html',
        bindings: {
            repository: "="
        },
        controller: function RepoListItemController($rootScope, $interval, $sce, githubRepoService, importService) {
            var $ctrl = this;
            var intervalTimer;

            $ctrl.$onInit = _init;
            $ctrl.importRepository = _importRepository;
            $ctrl.deleteRepository = _deleteRepository;


            function _init() {
                $ctrl.tooltipTitle = $ctrl.repository.summary_fields.provider.name + ' Repository';
                $ctrl.tooltipText = _tooltipText();
                $ctrl.viewImportLink = 'imports#/?github_user=' + $ctrl.repository.summary_fields.provider_namespace.name +
                                                '&github_repo=' + $ctrl.repository.original_name;
            }

            function _tooltipText() {
                var linkText = $ctrl.repository.summary_fields.provider_namespace.name + '/' + $ctrl.repository.original_name;
                var linkHref = '';
                var stars = $ctrl.repository.stargazers_count;
                var forks = $ctrl.repository.forks_count;
                var fullCommit = $ctrl.repository.commit;
                var commit = fullCommit ? fullCommit.substring(0, 7) : '';
                var commitMsg = $ctrl.repository.commit_message;

                if ($ctrl.repository.summary_fields.provider.name.toLowerCase() === 'github') {
                    linkHref = "https://github.com/" + linkText;
                }

                return $sce.trustAsHtml('<p><a target="_blank" href="' + linkHref + '">' + linkText + '</a></p>' +
                    '<p>Stars: ' + stars + '</p>' +
                    '<p>Forks: ' + forks + '</p>' +
                    '<p>Last Commit: (' + commit + ') ' + commitMsg + '</p>');
            }

            function _importRepository() {
                importService.imports.save({
                    'github_user': $ctrl.repository.github_user,
                    'github_repo': $ctrl.repository.github_repo,
                    'alternate_role_name': $ctrl.repository.role_name
                }).$promise.then(function (response) {
                    $ctrl.import = response.results[0];
                    return _queryStatus();
                }).then(function (response) {
                    _pollImportState();
                });
            }

            function _pollImportState() {
                intervalTimer = $interval(_queryStatus, 5000, 0, true)
            }

            function _queryStatus() {
                if ($ctrl.queryStatusInProgress) {
                    return;
                }

                $ctrl.queryStatusInProgress = true;
                return importService.imports.query({
                    repository: $ctrl.repository.id,
                    page_size: 1
                }).$promise.then(function (response) {
                    $ctrl.queryStatusInProgress = false;
                    if (response.results.length > 0) {
                        $ctrl.import = response.results[0];
                        if ($ctrl.import.state === 'FAILED' || $ctrl.import.state === 'SUCCESS') {
                            $interval.cancel(intervalTimer);
                        }
                    } else {
                        $ctrl.import = null;
                    }
                });
            }

            function _deleteRepository() {
                githubRepoService.delete({id: $ctrl.repository.id}).$promise.then(function() {
                    $rootScope.$emit('namespace.update', $ctrl.repository.summary_fields.namespace);
                })
            }
        }
    });


})(angular);
