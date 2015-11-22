/*
 * roleRemoveService.js
 */

 'use sctrict';

 (function(angular) {

    var mod = angular.module('roleRemoveSerivice', []);

    mod.factory('roleRemoveService', ['$resource', 'getCSRFToken', _factory]);

    function _factory($resource, getCSRFToken) {
        return  {
            delete: function(params) {
                var token = getCSRFToken(); 
                return $resource('/api/v1/removerole/', {}, {
                    'delete': { 'method': 'PUT', headers: { "X-CSRFToken": token }}
                }).delete(params);
            }
        };
    }

 })(angular);