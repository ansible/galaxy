/*
 * roleListController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
    
    var mod = angular.module('roleListController', ['ngResource']);

    mod.controller('RoleListCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        '$resource',
        '$window',
        'roleFactory',
        'roleSearchService',
        'queryStorageFactory',
        'my_info',
        'Empty',
        'SearchInit',
        'PaginateInit',
        'platformService',
        'queryParams',
        'fromQueryParams',
        _RoleListCtrl
    ]);

    function _RoleListCtrl(
        $scope,
        $routeParams,
        $location,
        $timeout,
        $resource,
        $window,
        roleFactory,
        roleSearchService,
        storageFactory,
        my_info,
        Empty,
        SearchInit,
        PaginateInit,
        platformService,
        queryParams,
        fromQueryParams) {

        var AVG_SCORE_SORT = 'average_score,name';

        //$scope.orderby={ sort_order: 'owner__username,name' };
        $scope.page_title = 'Browse Roles';
        $scope.my_info = my_info;

        $scope.list_data = {
            'list_filter'        : '',
            'num_pages'          : 1,
            'page'               : 1,
            'results_per_page'   : 8,
            'reverse'            : false,
            'platform'           : '',
            'selected_categories': [],
            'sort_order'         : '',
            'refresh'            : _refresh
        };

        $scope.orderby_options = [
            { value:"name", title:"Name" },
            { value:"username", title:"Author" },
            { value:"score", title:"Score" }
        ];

        $scope.page_range = [1];
        $scope.categories = [];
        $scope.roles = [];
        $scope.num_roles = 0;
        $scope.status = '';

        $scope.loading = 1;
        $scope.viewing_roles = 1;
        $scope.display_user_info = 1;
        $scope.searchSuggestions = [];
        
        // autocomplete functions
        $scope.onKeyUp = _onKeyUp;
        $scope.search = _search;
        $scope.suggestionSearch = _suggestionSearch;
        
        PaginateInit({ scope: $scope });

        var restored_query = storageFactory
            .restore_state('role_list', queryParams($scope.list_data));

        $scope.list_data = angular.extend({},
            $scope.list_data,
            fromQueryParams(restored_query));

        
        function _refresh(_params) {
            $scope.loading = 1;
            var params = {
                page: $scope.list_data.page,
                page_size: $scope.list_data.results_per_page,
            };
            if ($scope.list_data.sort_order) {
                params.order = $scope.list_data.sort_order;
            }
            if (_params) {
                angular.extend(params, _params);
            }
            roleSearchService.get(params)
                .$promise.then(function(data) {
                    $scope.roles = data.results;
                    $scope.status = "";
                    $scope.loading = 0;

                    $scope.list_data.page = parseInt(data['cur_page']);
                    $scope.list_data.num_pages = parseInt(data['num_pages']);

                    // Bug in API causes it to not return `cur_page` or `num_pages` when less than a single page of data in database
                    // This causes the query to be cached with null values, which means subsequent requests return no data
                    // Defaulting these values to 1 ensures we never cache the query with null values
                    $scope.list_data.page = $scope.list_data.page || 1;
                    $scope.list_data.num_pages = $scope.list_data.num_pages || 1;
                    
                    $scope.num_roles = parseInt(data['count']);
                    $scope.list_data.page_range = [];
                    $scope.setPageRange();
                });
        }

        _refresh();

        var suggestions = $resource('/api/v1/search/:object/', { 'object': '@object' }, {
            'tags': { method: 'GET', params:{ object: 'tags' }, isArray: false},
            'platforms': { method: 'GET', params:{ object: 'platforms' }, isArray: false}
        });

        function _onKeyUp(searchValue) {
            var resp = {}
            // search for tag matches
            suggestions.tags({autocomplete: searchValue }).$promise.then(function(data) {
                resp.tags = [];
                if (data.results.length) {
                    resp.tags.push({ type: 'tag', 'class': 'title', name: 'Tags'});
                    angular.forEach(data.results, function(result) {
                        resp.tags.push({ type: 'tag', 'class':'detail', name: result.tag });
                    });
                }
            }).then(function() {
                // search for platform matches
                suggestions.platforms({autocomplete:  searchValue }).$promise.then(function(data) {
                    resp.platforms = [];
                    if (data.results.length) {
                        resp.platforms.push({ type: 'platform', 'class': 'title', name: 'Platforms' });
                        angular.forEach(data.results, function(result) {
                            resp.platforms.push({ type: 'platform', 'class': 'detail', name: result.name });
                        });
                    }
                }).then(function() {
                    // Stich together the results
                    $scope.suggestions = [];
                    if (resp.tags.length)
                        angular.copy(resp.tags, $scope.suggestions);
                    if (resp.platforms.length)
                        angular.copy(resp.platforms, $scope.suggestions);
                });
            });
        }

        function _search(searchValue) {
            $scope.list_data.page = 1;
            _refresh({ autocomplete: searchValue });
        }

        function _suggestionSearch(suggestion) {
            if (suggestion.type ===  'tag') {
                _refresh({ tags: suggestion.name });
            } else if (suggestion.type == 'platform') {
                _refresh({ platforms: suggestion.name });
            }
        }

        function _windowResize() {
            $timeout(function() {
                var wh = $($window).height();
                var gpt = $('#galaxy-page-title').outerHeight();
                var gn = $('#galaxy-navbar').outerHeight();
                var ph = $('#galaxy-page-row').outerHeight();
                var bl = $('#galaxy-blue-line').outerHeight();
                var f = $('#galaxy-footer').outerHeight();
                var rl = $('#role-list-search').outerHeight();
                console.log('window height: ' + wh);
                console.log('page title: ' + gpt);
                console.log('galaxy navbar: ' + gn);
                console.log('page row: ' + ph);
                var height = wh - gpt - gn - ph - bl - f - rl + 45;
                console.log('height: ' + height);
                $('#role-list-results').height(height);
            }, 1000);
        }
        $($window).resize(_windowResize);
        _windowResize();
    }
})(angular);