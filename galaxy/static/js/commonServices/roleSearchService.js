
/*
 * roleSearchService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('roleSearchService', ['ngResource']);

    mod.factory('roleSearchService', ['$resource', _factory]);

    function _factory($resource) {
        return $resource('/api/v1/search/roles', null,{
            get: {
                method: 'GET',
                isArray: false
            }
        });
    }

})(angular);