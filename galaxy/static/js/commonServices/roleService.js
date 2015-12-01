/*
 * roleService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('roleService', ['ngResource','galaxyUtilities']);
        
    mod.factory('roleService', ['$resource','getCSRFToken', _factory]);

    function _factory($resource, getCSRFToken) {
        return {
            "get": _getRole,
            "delete": _deleteRole,
        };

        function _getRole(params) {
            return $resource('/api/v1/search/roles/').get(params);
        }

        function _deleteRole(id) {
            return $resource('api/v1/roles/:id/', { 'id': id }, {
                "delete": { method: 'DELETE', headers: { "X-CSRFToken": token }}
            }).delete();
        }
    }

})(angular);
