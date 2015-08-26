/*
 * roleListController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
    
    var mod = angular.module('roleListController', []);

    mod.controller('RoleListCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        'roleFactory',
        'categoryFactory',
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
        roleFactory,
        categoryFactory,
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
            'sort_order'         : 'owner__username,name',
            'refresh'            : _refresh
        };

        $scope.page_range = [1];
        $scope.categories = [];
        $scope.roles = [];
        $scope.num_roles = 0;
        $scope.status = '';

        $scope.loading = 1;
        $scope.viewing_roles = 1;
        $scope.display_user_info = 1;
        
        PaginateInit({ scope: $scope });

        $scope.getCategories = function () {
            categoryFactory.getCategories('name',true)
                .success( function (data) {
                    $scope.categories = data;
                    var tags = [];
                    for (var i=0; i < data.length; i++) {
                        tags.push(data[i].name);
                    }
                    $scope.tags = tags;
                    $('#categories-select').select2({
                        width: '100%',
                        tags: tags,
                        placeholder: 'Categories',
                        tokenSeparators: [",", " "]
                        });
                    $('#categories-select').on('change', function() { $scope.change_category() });
                    if ($scope.list_data.selected_categories.length > 0) {
                        $('#categories-select').val($scope.list_data.selected_categories).trigger('change');
                    }
                    })
                .error( function (error) {

                      // ERROR HANDLING!!!

                    });
        };

        $scope.is_selected = function(item) {
            if ($scope.list_data.selected_categories.indexOf(item) != -1)
                return true;
            else
                return false;
        };

        // Category field tag change
        $scope.change_category = function() {
            $scope.list_data.selected_categories = $('#categories-select').select2('val');
            $scope.list_data.refresh();
        };

        // User clicked on a tag link.
        $scope.pick_category = function(val) {
            var tags = '';
            var found = false;
            for (var i=0; i < $scope.list_data.selected_categories.length; i++) {
                if ($scope.list_data.selected_categories[i] == val) {
                   found = true;
                   break;
                }
            }
            if (!found) {
               $scope.list_data.selected_categories.push(val);
               $('#categories-select').val($scope.list_data.selected_categories).trigger("change");
            }
        };

        $scope.toggle_category = function(item) {
            var pos = $scope.list_data.selected_categories.indexOf(item);
            if (pos != -1) {
                $scope.list_data.selected_categories.splice(pos, 1);
            } else {
                $scope.list_data.selected_categories.push(item)
            }
            $location.path('roles');
            $scope.list_data.refresh();
        };

        $scope.clear_categories = function() {
            $location.path('roles');
            $scope.list_data.selected_categories = [];
            $scope.list_data.page = 1;
            $scope.list_data.refresh();
        };

        $scope.selectPlatform = function() {
            $scope.list_data.platform = ($scope.sort.platform && $scope.sort.platform.value) ? $scope.sort.platform.value : null;
            $scope.list_data.refresh();
        };

        var restored_query = storageFactory
            .restore_state('role_list', queryParams($scope.list_data));

        $scope.list_data = angular.extend({},
                $scope.list_data,
                fromQueryParams(restored_query));

        if ($routeParams.category_name) {
            $scope.list_data.selected_categories = [$routeParams.category_name];
        }

        SearchInit({
            scope: $scope,
            placeHolder: 'Search role name',
            showSearchIcon: ($scope.list_data.list_filter) ? false : true,
            sortOptions: [
                { value: AVG_SCORE_SORT, label: 'Average Score' },
                { value: 'created', label: 'Created On Date' },
                { value: 'owner__username,name', label: 'Owner Name' },
                { value: 'name', label: 'Role Name' }
            ],
            platforms: platformService.getPlatforms().then(function(data) {
                $scope.platforms = data;
            }),
            sortOrder: $scope.list_data.sort_order
        });

        $scope.getCategories();
        $scope.list_data.refresh();

        function _refresh(_change) {
            $scope.loading = 1;

            $scope.list_data.sort_order = $scope.getSortOrder();  //Check if user changed sort order

            if (_change === 'SortOrderSelect' && $scope.list_data.sort_order === AVG_SCORE_SORT) {
                // Sorting by Average Score should default to reverse (or descending) order
                $scope.list_data.reverse = true;
            }
            else if (_change === 'SortOrderSelect') {
                $scope.list_data.reverse = false;
            }

            storageFactory.save_state('role_list', queryParams($scope.list_data));

            roleFactory.getRoles(
                $scope.list_data.page,
                $scope.list_data.selected_categories,
                $scope.list_data.results_per_page,
                $scope.list_data.sort_order,
                $scope.list_data.list_filter,
                $scope.list_data.reverse,
                $scope.list_data.platform
            ).success(_refreshSuccess).error(_refreshError);

            function _refreshSuccess(data) {
                _uniquePlatforms(data.results);
                $scope.roles = data['results'];
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

                $scope.status = "";
                $scope.loading = 0;

                // Force window back to the top
                window.scrollTo(0, 0);
            }

            function _refreshError(error) {
                $scope.roles = [];
                $scope.list_data.page = 1;
                $scope.list_data.num_pages = 1;
                $scope.list_data.page_range = [1];
                $scope.num_roles = 0;
                $scope.status = 'Unable to load roles list: ' + error.message;
                $scope.loading = 0;
            }
        }

        function _uniquePlatforms(roles) {
            angular.forEach(roles, function(role) {
                var dict = {};
                angular.forEach(role.summary_fields.platforms, function(platform) {
                    dict[platform.name] = 0;
                });
                role.platforms = Object.keys(dict);
            });
        }
    }
})(angular);