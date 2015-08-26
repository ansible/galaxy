/*
 * userListController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('userListController', []);

    mod.controller('UserListCtrl', [
        '$scope',
        '$timeout',
        '$location',
        '$routeParams',
        'userFactory',
        'queryStorageFactory',
        'my_info',
        'SearchInit',
        'PaginateInit',
        'Stars',
        'queryParams',
        'fromQueryParams',
        _userListCtrl
    ]);

    function _userListCtrl(
        $scope,
        $timeout,
        $location,
        $routeParams,
        userFactory,
        storageFactory,
        my_info,
        SearchInit,
        PaginateInit,
        Stars,
        queryParams,
        fromQueryParams) {

        var AVG_SCORE_SORT = 'avg_role_score,username',
            NUM_ROLES_SORT = 'num_roles,username',
            NUM_RATINGS_SORT = 'num_ratings,username';

        $scope.page_title = 'Browse Users';
        $scope.my_info = my_info;

        $scope.list_data = {
            'list_filter'        : '',
            'num_pages'          : 1,
            'page'               : 1,
            'results_per_page'   : 10,
            'reverse'            : false,
            'selected_categories': [],
            'sort_order'         : 'username',
            'refresh'            : _refresh
        };

        $scope.page_range = [1];
        $scope.categories = [];
        $scope.users = [];
        $scope.num_users = 0;
        $scope.status = '';

        $scope.loading = 1;
        $scope.viewing_users = 1;

        PaginateInit({ scope: $scope });

        $scope.hover = function(idx, fld, val) {
            $scope[fld + '_hover_' + idx] = val;
        };

        var restored_query = storageFactory
            .restore_state('user_list', queryParams($scope.list_data));

        $scope.list_data = angular.extend({},
                $scope.list_data,
                fromQueryParams(restored_query));

        if ($routeParams.sort_order) {
            switch ($routeParams.sort_order) {
                case 'sort-by-community-score':
                    $scope.list_data.sort_order = 'avg_role_score,username';
                    $scope.list_data.reverse = true;
                    break;
                case 'sort-by-joined-on-date':
                    $scope.list_data.sort_order = 'date_joined,username';
                    $scope.list_data.reverse = true;
                    break;
                case 'sort-by-top-reviewers':
                    $scope.list_data.sort_order = 'karma,username';
                    $scope.list_data.reverse = true;
                    break;
            }
        }

        SearchInit({
            scope: $scope,
            placeHolder: 'Search user',
            showSearchIcon: ($scope.list_data.list_filter) ? false : true,
            sortOptions: [
                { value: AVG_SCORE_SORT, label: 'Average Role Score' },
                { value: 'date_joined,username', label: 'Date Joined' },
                { value: NUM_RATINGS_SORT, label: 'Number of Ratings' },
                { value: NUM_ROLES_SORT, label: 'Number of Roles' },
                { value: 'username', label: 'Username' }
                ],
            sortOrder: $scope.list_data.sort_order
        });

        $scope.list_data.refresh();

        return;


        function _refresh(_change) {
            $scope.list_data.sort_order = $scope.getSortOrder();
            $scope.loading = 1;

            if (_change === 'SortOrderSelect' &&
                ($scope.list_data.sort_order === AVG_SCORE_SORT || $scope.list_data.sort_order === NUM_ROLES_SORT ||
                    $scope.list_data.sort_order === NUM_RATINGS_SORT)) {
                // Sorting by Average Score ||s Number of Roles should default to reverse (or descending) order
                $scope.list_data.reverse = true;
            }
            else if (_change === 'SortOrderSelect') {
                $scope.list_data.reverse = false;
            }

            storageFactory.save_state('user_list', queryParams($scope.list_data));

            userFactory.getUsers(
                $scope.list_data.page,
                $scope.list_data.results_per_page,
                $scope.list_data.sort_order,
                $scope.list_data.reverse,
                $scope.list_data.list_filter
            ).success(_refreshSuccess).error(_refreshError);

            function _refreshSuccess(data) {
                for (var i=0; i < data['results'].length; i++) {
                    data['results'][i].karma_range = Stars(data['results'][i].karma);
                    data['results'][i].avg_rating_range = Stars(data['results'][i].avg_rating);
                    data['results'][i].avg_role_score_range = Stars(data['results'][i].avg_role_score);
                    data['results'][i].avg_role_aw_score_range = Stars(data['results'][i].avg_role_score);
                    if (data['results'][i].summary_fields.ratings.length > 0) {
                        data['results'][i].rating_range = Stars(data['results'][i].summary_fields.ratings[0].score);
                    }
                    else {
                        data['results'][i].rating_range = Stars(0);
                    }
                }
                $scope.users = data['results'];

                $scope.list_data.page = parseInt(data['cur_page']);
                $scope.list_data.num_pages = parseInt(data['num_pages']);
                $scope.num_users = parseInt(data['count']);
                $scope.list_data.page_range = [];
                $scope.setPageRange();

                $scope.status = "";
                $scope.loading = 0;

                // Force window back to the top
                window.scrollTo(0, 0);
            }

            function _refreshError(error) {
                $scope.users = [];
                $scope.num_users = 0;
                $scope.list_data.page = 1;
                $scope.list_data.num_pages = 1;
                $scope.list_data.page_range = [1];
                $scope.status = 'Unable to load users list: ' + error.message;
                $scope.loading = 0;
            }
        }
    }

})(angular);
