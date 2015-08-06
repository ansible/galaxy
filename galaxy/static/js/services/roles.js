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

(function(angular) {
    angular.module('roleServices', ['ngResource'])
        .factory('roleFactory', ['$http','$cookies', _factory]);

    function _factory($http, $cookies) {

        $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;

        return {
            getRoles: _getRoles,
            getRolesTop: _getRolesTop,
            getRole: _getRole,
            getLatest: _getLatest,
            deleteRole: _deleteRole,
        };

        function _getRoles(page, selected_categories, results_per_page, sort_order, filter, reverse, platform) {
            var url = '/api/v1/roles/?page=' + page + '&page_size=' + results_per_page;
            if (selected_categories.length > 0) {
                for (var i in selected_categories) {
                    url += '&chain__categories__name=' + selected_categories[i];
                }
            }
            if (filter && filter != '')
                url += '&name__icontains=' + filter;

            if (platform)
                url += '&platforms__name=' + platform;

            if (reverse) {
                var parts = sort_order.split(',')
                for (var part in parts) {
                    parts[part] = '-' + parts[part];
                }
                sort_order = parts.join(',');
            }
            url += '&order_by=' + sort_order
            return $http.get(url);
        }

        function _getRolesTop(page, results_per_page, sort_order, reverse) {
            var url = '/api/v1/roles/top/?page=' + page + '&page_size=' + results_per_page;
            if (reverse) {
                var parts = sort_order.split(',')
                for (var part in parts) {
                    parts[part] = '-' + parts[part];
                }
                sort_order = parts.join(',');
            }
            url += '&order_by=' + sort_order
            return $http.get(url);
        }

        function _getRole(id) {
            return $http.get('/api/v1/roles/' + id + '/');
        }

        function _getLatest(page, results_per_page, sort_order, reverse) {
            if (reverse) {
                sort_order = '-' + sort_order
            }
            return dataFactory.getRoles(page, [], results_per_page, sort_order);
        }

        function _deleteRole(id) {
            var url = '/api/v1/roles/'+id+'/'
            return $http.delete(url);
        }
    }

})(angular);
