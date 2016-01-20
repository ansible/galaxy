/*
 * exploreController.js
 * 
 * (c) 2012-2015, Ansible, Inc.
 *
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
            $resource('/api/v1/search/top_contributors/').get().$promise.then(function(response) {
                $scope.topContributors = response.results;
                $scope.loading.topContributors = false;
            });
        }
    }

})(angular);