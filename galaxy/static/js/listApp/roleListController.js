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
            'results_per_page'   : 10,
            'reverse'            : false,
            'platform'           : '',
            'selected_categories': [],
            'sort_order'         : '',
            'refresh'            : _refresh
        };

        $scope.orderOptions = [
            { value:"name", title:"Name" },
            { value:"username", title:"Author" },
            { value:"-average_score", title:"Score" }
        ];

        $scope.searchTypeOptions = [
            'Keyword',
            'Platform',
            'Tag'
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
        $scope.topTags = [];
        
        // autocomplete functions
        $scope.search = _search;
        $scope.searchSuggestion = _searchSuggestion;
        $scope.searchSuggesions = [];

        $scope.activateTag = _activateTag;
        $scope.changeOrderby = _changeOrderby;
        
        PaginateInit({ scope: $scope });

        var restored_query = storageFactory
            .restore_state('role_list', queryParams($scope.list_data));

        $scope.list_data = angular.extend({},
            $scope.list_data,
            fromQueryParams(restored_query));

        var suggestions = $resource('/api/v1/search/:object/', { 'object': '@object' }, {
            'tags': { method: 'GET', params:{ object: 'tags' }, isArray: false },
            'platforms': { method: 'GET', params:{ object: 'platforms' }, isArray: false}
        });
        
        var lazy_resize = _.debounce(_windowResize, 300);
        $($window).resize(lazy_resize);

        $timeout(function() {
            _windowResize();
            _topTags();
        }, 300);

        return; 

        function _activateTag(tag) {
            tag.active = !tag.active;
            _refresh();
        }

        function _topTags() {
            suggestions.tags({ order: '-roles', page: 1, page_size: 15 }).$promise.then(function(data) {
                $scope.topTags = data.results;
            });
        }

        function _changeOrderby() {
            _refresh();
        }

        function _refresh(_params, _callback) {
            $scope.loading = 1;
            $scope.roles = [];
            
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
            console.log('search!');
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

                    if (_callback) {
                        _callback();
                    }
                });
        }

        function _getActiveTags() {
            var result = '';
            var tags = $scope.topTags.filter(function(tag) {
                return tag.active;
            });
            tags.forEach(function(tag) {
                result += tag.tag + ',';
            });
            return result.replace(/,$/, '');
        }

        function _deactivateTags() {
            $scope.topTags.forEach(function(tag) {
                tag.active = false;
            });
        }

        function _search(_keywords, _orderby) {
            $scope.list_data.page = 1;
            var tags = [], platforms = [], keywords = [], params = {};
            angular.forEach(_keywords, function(keyword) {
                if (keyword.type === 'Tag') {
                    tags.push(keyword.value);
                } else if (keyword.type === 'Platform') {
                    platforms.push(keyword.value);
                } else {
                    keywords.push(keyword.value);
                }
            });
            if (tags.length) {
                params.tags = tags.join(' ');
            }
            if (platforms.length) {
                params.platforms = platforms.join(' ');
            }
            if (keywords.length) {
                params.autocomplete = keywords.join(' ');
            }
            if (_orderby) {
                params.order = _orderby.value;
            }
            console.log(params);
            _refresh(params);
        }

        function _searchSuggestion(type, value) {
            $scope.searchSuggestions = [];
            if (type ===  'Tag' && value) {
                suggestions.tags({ autocomplete: value}).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Tag',
                            name: result.tag
                        });
                    });
                });
                console.log($scope.searchSuggestions);
            } else if (type === 'Platform' && value) {
                suggestions.platforms({ autocomplete: value }).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Platform',
                            name: result.name
                        });
                    });
                });
            }
        }

        function _windowResize(skipSearch) {
            var calc = {
                window_height: $($window).height(),
                element_heights: [
                    $('#galaxy-page-title').outerHeight(),
                    $('#galaxy-navbar').outerHeight(),
                    100,
                    //$('#galaxy-blue-line').outerHeight() || 10,
                    //$('#galaxy-footer').outerHeight(),
                    $('#role-list-search').outerHeight()
                ],
                results_width: $('#role-list-search').width()
            };
            var height = calc.window_height - calc.element_heights.reduce(function(prev, cur) {  return prev + cur; }, 0);
            console.log(calc.element_heights);
            console.log('height: ' + height + ' width: ' + calc.results_width);
            var rows = Math.floor(height / 200); 
            var cols = Math.floor(calc.results_width / 225);
            $scope.list_data.results_per_page = rows * cols;
            //$('#role-list-results').height(rows * 200 + ((rows - 1) * 10));
            //console.log('height: ' + (rows * 200 + ((rows - 1) * 10)));
            console.log('cols: ' + cols);
            console.log('rows: ' + rows);
            _refresh(null);
        }
    }
})(angular);