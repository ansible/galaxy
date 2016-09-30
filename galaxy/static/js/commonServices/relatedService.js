/* (c) 2012-2016, Ansible by Red Hat
 *
 * This file is part of Ansible Galaxy
 *
 * Ansible Galaxy is free software: you can redistribute it and/or modify
 * it under the terms of the Apache License as published by
 * the Apache Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Ansible Galaxy is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * Apache License for more details.
 *
 * You should have received a copy of the Apache License
 * along with Galaxy.  If not, see <http://www.apache.org/licenses/>.
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
            var results_per_page = params.page_size; 
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
