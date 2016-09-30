/* (c) 2012-2016, Ansible by Red Hat
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

    var mod = angular.module('roleService', ['ngResource','galaxyUtilities']);
        
    mod.factory('roleService', ['$resource','$analytics','getCSRFToken', _factory]);

    function _factory($resource, $analytics, getCSRFToken) {
        var token = getCSRFToken();
        return {
            "get": _getRole,
            "delete": _deleteRole,
            "getReadMe": _getReadMe
        };

        function _getRole(params) {
            return $resource('/api/v1/search/roles/').get(params);
        }
        function _deleteRole(params) {
            $analytics.eventTrack('delete', {
                category: params.github_user + '/' + params.github_repo
            });
            return $resource('/api/v1/removerole/', null, {
                "delete": { method: 'DELETE', headers: { "X-CSRFToken": token }}
            }).delete(params);
        }
        function _getReadMe(id) {
            return $resource('/api/v1/roles/:id/', { 'id': id }).get().$promise.then(function(response) {
                return response.readme_html;
            });
        }
    }

})(angular);
