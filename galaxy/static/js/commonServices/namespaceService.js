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

    var mod = angular.module('namespaceService', ['ngResource', 'galaxyUtilities']);

    mod.factory('namespaceService', ['$resource', 'getCSRFToken', _factory]);

    function _factory($resource, getCSRFToken) {
        var token = getCSRFToken();
        return $resource('/api/v1/namespaces/:namespaceId/', {'namespaceId': _getId}, {
            'get':     {method: 'GET'},
            'query':   {method: 'GET', isArray:false},
            'save':    {method: 'POST', headers: {"X-CSRFToken": token}},
            'update':  {method: 'PUT', headers: {"X-CSRFToken": token}},
            'delete':  {method: 'DELETE', headers: {"X-CSRFToken": token}}
        });

        function _getId(data) {
            if (data) {
                return data.id;
            }
        }
    }

})(angular);
