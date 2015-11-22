/*
 * githubRepoService.js
 *
 */

 'use strict';

 (function(angular) {

    var mod = angular.module('githubRepoService', []);

    mod.factory('githubRepoService', ['$resource', _factory]);

    function _factory($resource) {

        return $resource('/api/v1/repolist');
    }


 })(angular);

