/* (c) 2012-2018, Ansible by Red Hat
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

    var mod = angular.module('exploreController', []);

    mod.controller('ExploreCtrl', [
        '$scope',
        '$timeout',
        '$resource',
        'roleSearchService',
        'tagService',
        _controller
    ]);

    function _controller($scope, $timeout, $resource, roleSearchService, tagService) {

        $scope.page_title = 'Explore';
        $scope.results_per_page = 10;

        $scope.loading = {
            tags: true,
            mostStarred: true,
            mostWatched: true,
            mostDownloaded: true,
            newRoles: true,
            topContributors: true
        };

        _getTags();
        _getMostStarredRoles();
        _getMostWatchedRoles();
        _getNewRoles();
        _getMostDownloaded();
        _getTopContributors();
        
        return;


        function _getTags() {
            tagService.get({ order: '-roles' }).$promise.then(function(response) {
                $scope.tags = response.results;
                $scope.loading.tags = false;
            });
        }

        function _getMostStarredRoles() {
            roleSearchService.get({
                'order_by': '-stargazers_count'
            }).$promise.then(function(response) {
                $scope.mostStarred = response.results;
                $scope.loading.mostStarred = false;
            });
        }

        function _getMostWatchedRoles() {
            roleSearchService.get({
                'order_by': '-watchers_count'
            }).$promise.then(function(response) {
                $scope.mostWatched = response.results;
                $scope.loading.mostWatched = false;
            });
        }

        function _getNewRoles() {
            roleSearchService.get({
                'order_by': '-created'
            }).$promise.then(function(response) {
                $scope.new_roles = response.results;
                $scope.loading.newRoles = false;
            });
        }

        function _getMostDownloaded() {
            roleSearchService.get({
                'order_by': '-download_count'
            }).$promise.then(function(response) {
                $scope.mostDownloaded = response.results;
                $scope.loading.mostDownloaded = false;
            });
        }

        function _getTopContributors() {
            $resource('/api/v1/search/top_contributors/').get({ page: 1 }).$promise.then(function(response) {
                $scope.topContributors = response.results;
                $scope.loading.topContributors = false;
            });
        }
    }

})(angular);
