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

    var mod = angular.module('namespaceEditController', []);

    mod.controller('NamespaceEditCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        'namespaceFormService',
        'namespace',
        _NamespaceEditCtrl
    ]);

    function _NamespaceEditCtrl(
        $scope,
        $routeParams,
        $location,
        $timeout,
        namespaceFormService,
        namespace
        ) {

        $scope.page_title = 'My Content';
        $scope.page_subtitle = 'Modify Galaxy Namespace';

        $scope.namespace  = {
            id: namespace.id,
            name: namespace.name,
            description: namespace.description,
            location: namespace.location,
            avatar_url: namespace.avatar_url,
            company: namespace.company,
            email: namespace.email,
            html_url: namespace.html_url,
            owners: namespace.summary_fields.owners,
            provider_namespaces: namespace.summary_fields.provider_namespaces,
            active: namespace.active
        };

        namespaceFormService($scope, 'update');
    }

})(angular);
