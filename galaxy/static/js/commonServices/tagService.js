/*
 * tagService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {
  
    var mod = angular.module('tagService', ['ngResource']);
 
    mod.factory('tagService', ['$resource', _factory]);
  
    function _factory($resource) {
        return $resource('/api/v1/search/tags/', null, {
            get: { method: 'GET', isArray: false },
            query: { method: 'GET', isArray: false }
        });
    }

})(angular);
