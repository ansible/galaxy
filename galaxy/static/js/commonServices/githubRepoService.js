/*
 * githubRepoService.js
 *
 */

 'use strict';

 (function(angular) {

    var mod = angular.module('githubRepoService', []);

    mod.factory('githubRepoService', ['$resource', _factory]);

    function _factory($resource) {

        return {
            get: function(params) {
                return $resource('/api/v1/repos/list/?page_size=1000').get(params);
            },
            refresh: function(params) {
                return $resource('/api/v1/repos/refresh/').get(params);
            }
        }
    }


 })(angular);

