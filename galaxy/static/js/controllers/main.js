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

/* Controllers */

var mainControllers = angular.module('mainControllers', []);

mainControllers.controller('MainCtrl', ['$scope', 'roleFactory', 'userFactory', 'categoryFactory',
function($scope, roleFactory, userFactory, categoryFactory) {
    
    $scope.page_title = 'Explore';
    $scope.results_per_page = 10;
    $scope.loading = 0;
    
    $scope.data_names = ["categories","top_roles","new_roles","top_users","top_reviewers","new_users"];

    $scope.restore_state = function () {
        $scope.data_names.forEach(function (entry) {
            console.log("entry is "+entry);
            var default_sort_col = '';
            var more_link = '';
            var data_function = null;
            if (entry == 'categories') {
                default_sort_col = 'num_roles';
                more_link = '/list#/roles/';
                data_function = $scope.getCategories;
            } 
            else if (entry == 'top_roles') {
                default_sort_col = 'average_score';
                more_link = '/list#/roles/sort/sort-by-community-score';
                data_function = $scope.getTopRoles;
            } 
            else if (entry == 'new_roles') {
                default_sort_col = 'created';
                more_link = '/list#/roles/sort/sort-by-created-on-date';
                data_function = $scope.getNewRoles;
            }
            else if (entry == 'top_users') {
                default_sort_col = 'avg_role_score';
                more_link = '/list#/users/sort/sort-by-community-score';
                data_function = $scope.getTopUsers;
            } 
            else if (entry == 'top_reviewers') {
                default_sort_col = 'karma';
                more_link = '/list#/users/sort/sort-by-top-reviewers';
                data_function = $scope.getTopReviewers;
            }
            else if (entry == 'new_users') {
                default_sort_col = 'date_joined';
                more_link = '/list#/users/sort/sort-by-joined-on-date';
                data_function = $scope.getNewUsers;
            }
            /*
            if (typeof(Storage) !== "undefined" && localStorage[entry]) { 
                //if local storage is available, and we previously stored a value
                $scope[entry] = JSON.parse(localStorage[entry]);
            }
            else {
            */
                $scope[entry] = {
                    'page': 1,
                    'data': [],
                    'sort_col': default_sort_col,
                    'reverse': true,
                    'more_link' : more_link,
                    'data_function': data_function
                    }
            //}
            });
        };

    if ($scope.removeSaveState) {
        $scope.removeSaveState();
    }
    $scope.removeSaveState = $scope.$on('saveState', function(e, entry) {
        if (typeof(Storage) !== "undefined") {
            //localStorage.setItem(entry, JSON.stringify($scope[entry])); 
        }
        });
    
    $scope.toggle_item = function (item, sort_col) {
        if (item.sort_col != sort_col) {
            item.sort_col = sort_col;
            item.data_function();
        }
        };

    $scope.getCategories = function () {
        categoryFactory.getCategories(
            $scope.categories.sort_col,
            $scope.categories.reverse
            )
            .success(function (data) {
                $scope.categories.data = data.slice(0, $scope.results_per_page);
                $scope.$emit('saveState', 'categories');
                })
            .error(function (error) {
                });
        };

    $scope.getTopRoles = function () {
        roleFactory.getLatest(
            $scope.top_roles.page,
            $scope.results_per_page,
            $scope.top_roles.sort_col,
            $scope.top_roles.reverse
            )
            .success(function (data) {
                $scope.top_roles.data = data['results'];
                $scope.$emit('saveState', 'top_roles');
                })
            .error(function (error) {
                });
        };

    $scope.getNewRoles = function () {
        roleFactory.getLatest(
            $scope.new_roles.page,
            $scope.results_per_page,
            $scope.new_roles.sort_col,
            $scope.new_roles.reverse
            )
            .success(function (data) {
                $scope.new_roles.data = data['results'];
                $scope.$emit('saveState', 'new_roles');
                })
            .error(function (error) {
                });
        };

    $scope.getTopUsers = function () {
        userFactory.getUsers(
            $scope.top_users.page,
            $scope.results_per_page,
            $scope.top_users.sort_col,
            $scope.top_users.reverse
            )
            .success(function (data) {
                $scope.top_users.data = data['results'];
                $scope.$emit('saveState', 'top_users');
                })
            .error(function (error) {
                });
        };

    $scope.getTopReviewers = function () {
        userFactory.getUsers(
            $scope.top_reviewers.page,
            $scope.results_per_page,
            $scope.top_reviewers.sort_col,
            $scope.top_reviewers.reverse
            )
            .success(function (data) {
                $scope.top_reviewers.data = data['results'];
                $scope.$emit('saveState', 'top_reviewers');
                })
            .error(function (error) {
                });
        };

    $scope.getNewUsers = function () {
        userFactory.getUsers(
            $scope.new_users.page,
            $scope.results_per_page,
            $scope.new_users.sort_col,
            $scope.new_users.reverse
            )
            .success(function (data) {
                $scope.new_users.data = data['results'];
                $scope.$emit('saveState', 'new_users');
                })
            .error(function (error) {
                });
    };

    $scope.restore_state();
    $scope.getCategories();
    $scope.getTopRoles();
    $scope.getNewRoles();
    $scope.getTopUsers();
    $scope.getTopReviewers();
    $scope.getNewUsers();
  }
]);

