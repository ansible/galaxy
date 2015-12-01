/*
 * githubRepoService.js
 *
 */

 'use strict';

 (function(angular) {

    var mod = angular.module('githubRepoService', ['currentUserService']);

    mod.factory('githubRepoService', ['$resource', 'currentUserService', 'getCSRFToken', _factory]);

    function _factory($resource, currentUserService, getCSRFToken) {

        var token = getCSRFToken();
            
        return {
            get: function(params) {
                params = (params) ? params : {};
                params.owner = currentUserService.id;
                return $resource('/api/v1/repos/list/?page_size=1000').get(params);
            },
            refresh: function(params) {
                return $resource('/api/v1/repos/refresh/').get(params);
            },
            subscribe: function(params) {
                return $resource('/api/v1/repos/subscriptions/', {}, {
                    'save': { 'method': 'POST', headers: { "X-CSRFToken": token }}
                }).save(params);
            },
            unsubscribe: function(params) {
                return $resource('/api/v1/repos/subscriptions/:id/', {'id': '@id'}, {
                    'delete': { 'method': 'DELETE', headers: { "X-CSRFToken": token }}
                }).delete(params);   
            },
            star: function(params) {
                return $resource('/api/v1/repos/stargazers/', {}, {
                    'save': { 'method': 'POST', headers: { "X-CSRFToken": token }}
                }).save(params);
            },
            unstar: function(params) {
                return $resource('/api/v1/repos/stargazers/:id/', {'id': '@id'}, {
                    'delete': { 'method': 'DELETE', headers: { "X-CSRFToken": token }}
                }).delete(params);  
            }
        }
    }

 })(angular);

