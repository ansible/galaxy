/*
# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
*/

'use strict';

var relatedService = angular.module('relatedService', ['ngResource']);
 
relatedService.factory('relatedFactory', ['$http',
    function($http){
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
        ]);
