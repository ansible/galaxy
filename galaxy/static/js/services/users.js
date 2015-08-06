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

    angular.module('userServices', ['ngResource'])
        .factory('userFactory', ['$http','$cookies', _factory]);

    function _factory($http, $cookies){

        $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;

        return {
            getUsers: _getUsers,
            getUser: _getUser,
            getUsersTop: _getUsersTop,
            getUserRelated: _getUserRelated,
            deleteUser: _deleteUser
        };


        function _getUsers(page, results_per_page, sort_order, reverse, filter) {
            var url = '/api/v1/users/?page=' + page + '&page_size=' + results_per_page;
            if (reverse) {
                sort_order = '-' + sort_order
            }
            url += '&order_by=' + sort_order;
            if (filter && filter != '') {
                url += '&or__username__icontains=' + filter + '&or__full_name__icontains=' + filter;
            }
            return $http.get(url);
        }

        function _getUsersTop(page, results_per_page, sort_order, reverse) {
            var url = '/api/v1/users/top/?page=' + page + '&page_size=' + results_per_page;
            if (reverse) {
                sort_order = '-' + sort_order
            }
            url += '&order_by=' + sort_order;
            return $http.get(url);
        }

        function _getUser(id) {
            return $http.get('/api/v1/users/' + id);
        }

        function _getUserRelated(url, page, results_per_page, sort_order, reverse) {
            var target_url = url + '?page=' + page + '&page_size=' + results_per_page;
            if (reverse) {
                sort_order = '-' + sort_order
            }
            target_url += '&order_by=' + sort_order;
            return $http.get(target_url);
        }

        function _deleteUser(id) {
            var url = '/api/v1/users/'+id+'/'
            return $http.delete(url);
        }
    }

})(angular);
