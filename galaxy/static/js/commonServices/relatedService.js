/*
 * relatedService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('relatedService', ['ngResource']);
 
    mod.factory('relatedFactory', ['$http', _factory]);

    function _factory($http){
        var dataFactory = {};
        dataFactory.getRelated = function(params) {
            var url = params.url; 
            var page = params.page; 
            var results_per_page = params.results_per_page; 
            var sort_order = params.sort_order; 
            var reverse = params.reverse; 
            var target_url = url + '?page=' + page + '&page_size=' + results_per_page;
            if (reverse) {
                sort_order = '-' + sort_order
            }
            target_url += '&order_by=' + sort_order;
            return $http.get(target_url);
            };
        return dataFactory; 
    }
    
})(angular);
