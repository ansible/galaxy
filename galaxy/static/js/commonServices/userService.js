/*
 * userService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    angular.module('userService', ['ngResource'])
        .factory('userFactory', ['$http','$cookies', _factory]);

    function _factory($http, $cookies){

        $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;

        return {
            getUsers: _getUsers,
            getUser: _getUser,
            getRoleContributors: _getRoleContributors,
            getRatingContributors: _getRatingContributors,
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

        function _getRatingContributors(page, results_per_page, sort_order, reverse) {
            var url = '/api/v1/users/ratingcontributors/?page=' + page + '&page_size=' + results_per_page;
            if (reverse) {
                sort_order = '-' + sort_order
            }
            url += '&order_by=' + sort_order;
            return $http.get(url);
        }

        function _getRoleContributors(page, results_per_page, sort_order, reverse) {
            var url = '/api/v1/users/rolecontributors/?page=' + page + '&page_size=' + results_per_page;
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
