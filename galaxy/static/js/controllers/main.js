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

    angular.module('mainControllers', [])
        .controller('MainCtrl', ['$scope', '$timeout', 'roleFactory', 'userFactory', 'categoryFactory', _controller]);

    function _controller($scope, $timeout, roleFactory, userFactory, categoryFactory) {

        $scope.page_title = 'Explore';
        $scope.results_per_page = 10;

        $scope.loading = {
            categories: 1,
            topRoles: 1,
            newRoles: 1,
            topUsers: 1,
            topReviewers: 1,
            newUsers: 1
        };

        $scope.toggle_item = function (item, sort_col) {
            if (item.sort_col != sort_col) {
                item.sort_col = sort_col;
                item.data_function();
            }
        };

        $timeout(function() {
            // give the partial templates a chance to load before we do this...
            _restoreState();
            _getCategories();
            _getTopRoles();
            _getNewRoles();
            _getTopUsers();
            _getTopReviewers();
            _getNewUsers();
        }, 300);

        return;


        function _restoreState() {
            var data_names = ["categories","top_roles","new_roles","top_users","top_reviewers","new_users"];
            data_names.forEach(function (entry) {
                var default_sort_col = '';
                var more_link = '';
                var data_function = null;
                if (entry === 'categories') {
                    default_sort_col = 'num_roles';
                    more_link = '/list#/roles/';
                    data_function = _getCategories;
                }
                else if (entry === 'top_roles') {
                    default_sort_col = 'average_score';
                    more_link = '/list#/roles/sort/sort-by-community-score';
                    data_function = _getTopRoles;
                }
                else if (entry === 'new_roles') {
                    default_sort_col = 'created';
                    more_link = '/list#/roles/sort/sort-by-created-on-date';
                    data_function = _getNewRoles;
                }
                else if (entry === 'top_users') {
                    default_sort_col = 'avg_role_score';
                    more_link = '/list#/users/sort/sort-by-community-score';
                    data_function = _getTopUsers;
                }
                else if (entry === 'top_reviewers') {
                    default_sort_col = 'num_ratings';
                    more_link = '/list#/users/sort/sort-by-top-reviewers';
                    data_function = _getTopReviewers;
                }
                else if (entry === 'new_users') {
                    default_sort_col = 'date_joined';
                    more_link = '/list#/users/sort/sort-by-joined-on-date';
                    data_function = _getNewUsers;
                }

                $scope[entry] = {
                    'page': 1,
                    'data': [],
                    'sort_col': default_sort_col,
                    'reverse': true,
                    'more_link' : more_link,
                    'data_function': data_function
                };
            });
        }

        function _getCategories() {
            categoryFactory.getCategories(
                $scope.categories.sort_col,
                $scope.categories.reverse
                )
                .success(function (data) {
                    $scope.categories.data = data.slice(0, $scope.results_per_page);
                    $scope.loading.categories = 0;
                })
                .error(function (error) {
                    $scope.loading.categories = 0;
                    $scope.categories.data = [];
                });
        }

        function _getTopRoles() {
            roleFactory.getLatest(
                $scope.top_roles.page,
                $scope.results_per_page,
                $scope.top_roles.sort_col,
                $scope.top_roles.reverse
                )
                .success(function (data) {
                    data['results'].forEach(function(row) {
                        row.average_score = parseFloat(row.average_score);
                    });
                    $scope.top_roles.data = data['results'];
                    $scope.loading.topRoles = 0;
                })
                .error(function (error) {
                    $scope.loading.topRoles = 0;
                    $scope.top_roles.data = 0;
                });
        }

        function _getNewRoles() {
            roleFactory.getLatest(
                $scope.new_roles.page,
                $scope.results_per_page,
                $scope.new_roles.sort_col,
                $scope.new_roles.reverse
                )
                .success(function (data) {
                    $scope.new_roles.data = data['results'];
                    $scope.loading.newRoles = 0;
                })
                .error(function (error) {
                    $scope.new_roles.data = [];
                    $scope.loading.newRoles = 0;
                });
        }

        function _getTopUsers() {
            userFactory.getUsers(
                $scope.top_users.page,
                $scope.results_per_page,
                $scope.top_users.sort_col,
                $scope.top_users.reverse
                )
                .success(function (data) {
                    data['results'].forEach(function(row) {
                        row.num_roles = parseInt(row.num_roles);
                        row.avg_role_score = parseInt(row.avg_role_score);
                    });
                    $scope.top_users.data = data['results'];
                    $scope.loading.topUsers = 0;
                })
                .error(function (error) {
                    $scope.top_users.data = [];
                    $scope.loading.topUsers = 0;
                });
        }

        function _getTopReviewers() {
            userFactory.getUsers(
                $scope.top_reviewers.page,
                $scope.results_per_page,
                $scope.top_reviewers.sort_col,
                $scope.top_reviewers.reverse
                )
                .success(function (data) {
                    data['results'].forEach(function(row) {
                        row.num_ratings = parseInt(row.num_ratings);
                    });
                    $scope.top_reviewers.data = data['results'];
                    $scope.loading.topReviewers = 0;
                })
                .error(function (error) {
                    $scope.top_reviewers.data = [];
                    $scope.loading.topReviewers = 0;
                });
        }

        function _getNewUsers() {
            userFactory.getUsers(
                $scope.new_users.page,
                $scope.results_per_page,
                $scope.new_users.sort_col,
                $scope.new_users.reverse
                )
                .success(function (data) {
                    $scope.new_users.data = data['results'];
                    $scope.loading.newUsers = 0;
                })
                .error(function (error) {
                    $scope.new_users.data = [];
                    $scope.loading.newUsers = 0;
                });
        }
    }

})(angular);
