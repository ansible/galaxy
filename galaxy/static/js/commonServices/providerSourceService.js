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

    var mod = angular.module('providerSourceService', ['ngResource']);

    mod.factory('providerSourceService', ['$resource', 'getCSRFToken', _factory]);

    function _factory($resource, currentUserService, getCSRFToken) {

        return {
            getRepoSources: function(params) {
                params = (params) ? params : {};
                params.owners = currentUserService.id;
                return $resource('/api/v1/providers/sources/:providerName/:name', {
                    providerName: params.providerName,
                    name: params.name
                }, {
                    get: {
                        method: 'GET',
                        isArray: true
                    }
                }).get(params);
            },
            query: function(params) {
                return $resource('/api/v1/providers/sources/', null, {
                    'get': { method: 'GET', isArray: true }
                }).get(params);
            }
        }
    }

})(angular);
