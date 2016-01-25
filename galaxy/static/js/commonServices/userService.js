/*
 * userService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('userService', ['ngResource']);
        
    mod.factory('userService', ['$resource', _factory]);

    function _factory($resource) {
        return $resource('/api/v1/users/');
    }

})(angular);
