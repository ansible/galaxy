/*
 * githubRepoService.js
 *
 */

 'use strict';

 (function(angular) {

    var mod = angular.module('githubRepoService', ['currentUserService']);

    mod.factory('githubRepoService', ['$resource', 'currentUserService', _factory]);

    function _factory($resource, currentUserService) {

        return {
            get: function(params) {
                params = (params) ? params : {};
                params.owner = currentUserService.id;
                return $resource('/api/v1/repos/list/?page_size=1000').get(params);
            },
            refresh: function(params) {
                return $resource('/api/v1/repos/refresh/').get(params);
            }
        }
    }


 })(angular);

