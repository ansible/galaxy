/*
 * userDetailController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */
 

'use strict';

(function(angular) {

    var mod = angular.module('userDetailController', []);

    mod.controller('UserDetailCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        'userFactory',
        'ratingFactory',
        'my_info',
        'Range',
        'relatedFactory',
        'Empty',
        'Stars',
        'PaginateInit',
        'queryParams',
        'fromQueryParams',
        'user',    
        _userDetailCtrl
    ]);

    function _userDetailCtrl(
        $scope,
        $routeParams,
        $location,
        userFactory,
        ratingFactory,
        my_info,
        Range,
        relatedFactory,
        Empty,
        Stars,
        PaginateInit,
        queryParams,
        fromQueryParams,
        user) {

        console.log(user);
        $scope.my_info = my_info;
        $scope.page_title = 'User Detail';
        $scope.showRoleName = true;
        $scope.my_info = my_info;

        $scope.list_data = {
            'roles' : {
                'list_filter'        : '',
                'num_pages'          : 1,
                'page'               : 1,
                'results_per_page'   : 10,
                'reverse'            : false,
                'selected_categories': [],
                'sort_order'         : 'name',
                'refresh'            : function() {
                    $scope.$emit('refreshRelated', 'roles', user.related.roles);
                    }
                },
            'ratings' : {
                'list_filter'        : '',
                'num_pages'          : 1,
                'page'               : 1,
                'results_per_page'   : 10,
                'reverse'            : true,
                'selected_categories': [],
                'sort_order'         : 'created',
                'refresh'            : function() {
                    $scope.$emit('refreshRelated', 'ratings', user.related.ratings);
                    }
                }
            };

        $scope.roles = [];
        $scope.ratings = [];

        PaginateInit({ scope: $scope });

        // controls if role info is displayed in the -display partials
        $scope.display_role_info = 1;
        $scope.display_user_info = 0;
        $scope.user = user;
        
        $scope.ratingHover = function(itm, label, flag) {
            $scope[label + '_' + 'hover' + '_' + itm] = flag;
        };

        $scope.addVote = function(id, direction) {
            ratingFactory.addVote(id, {'id':my_info.id}, direction)
                .success( function(data) {
                    $scope.$emit('refreshRelated', 'ratings', $scope.user.related.ratings);
                    })
                .error( function(error) {
                    console.error("failed to add a "+direction+" vote on rating id=" + id);
                    });
        };

        $scope.$on('refreshRelated', function(e, target, url) {
            $scope.list_data[target].url = url;
            relatedFactory.getRelated($scope.list_data[target])
                .success( function(data) {
                    $scope.list_data[target].page = parseInt(data['cur_page']);
                    $scope.list_data[target].num_pages = parseInt(data['num_pages']);
                    $scope.list_data[target].page_range = [];
                    $scope.setPageRange(target);

                    if (data['results'].length > 0 && !Empty(data['results'][0].reliability)) {
                        // Add 'ranges' to the data that we can pipe through ng-repeat to create a graphic
                        // representation of each rating.
                        for (var i=0; i < data['results'].length; i++) {
                            data['results'][i].reliability_range = Stars(data['results'][i].reliability);
                            data['results'][i].documentation_range = Stars(data['results'][i].documentation);
                            data['results'][i].code_quality_range = Stars(data['results'][i].code_quality);
                            data['results'][i].wow_factor_range = Stars(data['results'][i].wow_factor);
                            data['results'][i].score_range = Stars(data['results'][i].score);
                        }
                    }
                    $scope[target] = data['results'];
                    $scope.loading--;
                })
                .error(function (error) {
                    $scope.status = 'Unable to load related ' + target + ': ' + error.message;
                });
        });

        $scope.staffDeleteRating = function(id) {
            ratingFactory.deleteRating(id)
                .success(function (data) {
                    $scope.getUser();
                })
                .error(function (error) {
                    alert("Failed to remove rating "+id+", reason: "+error);
                });
        };

        $scope.staffDeleteUser = function(id) {
            userFactory.deleteUser(id)
                .success(function (data) {
                    $location.path('/users');
                })
                .error(function (error) {
                    alert("Failed to remove user "+id+", reason: "+error);
                });
        };

        $scope.loading = 2;
        $scope.list_data.roles.refresh();
        $scope.list_data.ratings.refresh();

    }

})(angular);