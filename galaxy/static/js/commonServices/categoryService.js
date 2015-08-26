/*
 * categoryService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {
  
    var mod = angular.module('categoryService', ['ngResource']);
 
    mod.factory('categoryFactory', ['$http', _factory]);
  
    function _factory($http) {
        var dataFactory = {};
        dataFactory.getCategories = function(sort_field, reverse) { 
            var url = '/api/v1/categories/?';
            if (reverse) {
                url += 'order_by=-' + sort_field;
            } else {
                url += 'order_by=' + sort_field;
            }
            return $http.get(url);
        };
        return dataFactory;
    }

})(angular);
