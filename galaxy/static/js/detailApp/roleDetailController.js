/*
 * roleDetailController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use list';

(function(angular) {

    var mod = angular.module('roleDetailController', []); 

    mod.controller('RoleDetailCtrl', [
        '$q',
        '$scope',
        '$routeParams',
        '$location',
        '$modal',
        '$compile',
        'roleFactory',
        'userFactory',
        'ratingFactory',
        'meFactory',
        'relatedFactory',
        'my_info',
        'Stars',
        'PaginateInit',
        'queryParams',
        'fromQueryParams',
        'role',
        _roleDetailCtrl
    ]);

    function _roleDetailCtrl(
        $q,
        $scope,
        $routeParams,
        $location,
        $modal,
        $compile,
        roleFactory,
        userFactory,
        ratingFactory,
        meFactory,
        relatedFactory,
        my_info,
        Stars,
        PaginateInit,
        queryParams,
        fromQueryParams,
        role) {

        $scope.page_title = 'Role Detail';
        $scope.showRoleName = false;
        $scope.my_info = my_info;

        $scope.list_data = {
            'ratings' : {
                'list_filter'        : '',
                'num_pages'          : 1,
                'page'               : 1,
                'results_per_page'   : 10,
                'reverse'            : false,
                'selected_categories': [],
                'sort_order'         : 'created',
                'refresh'            : function() {
                    $scope.$emit('getRelated', 'ratings', $scope.role.related.ratings);
                }
            }
        };

        $scope.role = role;
        $scope.ratings = [];
        $scope.display_user_info = 1;
        $scope.getRole = _getRole;
        $scope.$on('getRelated', _getRelated);
        $scope.showRatingDialog = _showRatingDialog;
        $scope.staffDeleteRating = _deleteRating;
        $scope.staffDeleteRole = _deleteRole;
        _getRelated(null, 'ratings', role.related.ratings);
        PaginateInit({'scope': $scope});

        return; 


        function _modalController ($scope, $modalInstance, role, ratingFactory, rating) {
            $scope.alerts = [];
            $scope.role = role;

            if (rating) {
                $scope.rating = rating;
            } else {
                $scope.rating = {
                    comment: null,
                    score: ''
                };
            }

            $scope.closeAlert = function(index) {
                $scope.alerts.splice(index, 1);
            };

            $scope.ok = function () {
                var post_data = {
                    'pk': $scope.role.id,
                }
                angular.extend(post_data, $scope.rating);
                post_data.score = parseInt(post_data.score);
                post_data.comment = (post_data.comment) ? post_data.comment : "";
                console.log(post_data);
                ratingFactory.addRating(
                    role.related.ratings,
                    post_data)
                    .success(function(data) {
                        $modalInstance.close(true);
                    })
                    .error(function(data, status) {
                        var msg = '';
                        console.error(status);
                        if (status == 403) {
                            msg = 'You do not have permission to add a rating to this role.';
                        } else if(status == 409) {
                            msg = 'You appear to have already rated this role. If your rating is not visible, it may mean that an administrator has removed it for violating our terms of service. If you believe this was done in error, please contact us.';
                        } else {
                            msg = 'An unknown error occurred while trying to add your rating. Please wait a while and try again.';
                        }
                        $scope.alerts = [{type: 'danger','msg':msg}]
                    });
            };

            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        }

        function _deleteRating(id) {
            ratingFactory.deleteRating(id)
            .success(function (data) {
                $scope.getRole();
            })
            .error(function (error) {
                alert("Failed to remove rating "+id+", reason: "+error);
            });
        }

        function _deleteRole(id) {
            roleFactory.deleteRole(id)
            .success(function (data) {
                $location.path('/roles');
            })
            .error(function (error) {
                alert("Failed to remove role "+id+", reason: "+error);
            });
        }

        function _showRatingDialog() {
            if (!my_info.authenticated) 
                return;

            var modalInstance = $modal.open ({
                templateUrl: "/static/partials/add-rating.html",
                controller: _modalController,
                resolve: {
                    role: function() { return $scope.role; },
                    ratingFactory: function() { return ratingFactory; },
                    rating: function() {
                        var d = $q.defer();
                        ratingFactory.getMyRatingForRole(my_info.id, $scope.role.id)
                            .success(function (data) {
                                if (data.count > 0) {
                                    var res = data.results[0];
                                    var rating = {
                                        'id': res.id,
                                        'score': res.score,
                                        'comment': res.comment
                                    };
                                    d.resolve(rating);
                                } else {
                                    d.resolve(null);
                                }
                            })
                            .error(function (error) {
                                d.reject(error);
                            });
                        return d.promise;
                        }
                    }
                });

            modalInstance.result.then(function (result) {
                if (result) {
                    $scope.getRole();
                    }
                });
        }

        function _getRole() {
            roleFactory.getRole($routeParams.role_id)
                .success( function(data) {
                    $scope.role = data;
                    $scope.$emit('getRelated', 'ratings', data.related.ratings);
                })
                .error( function(error) {
                    $scope.status = 'Unable to load role: ' + error.message;
                });
        }

        function _getRelated(e, target, url) {
            $scope.list_data[target].url = url;
            relatedFactory.getRelated($scope.list_data[target])
                .success( function(data) {
                    $scope.list_data[target].page = parseInt(data['cur_page']);
                    $scope.list_data[target].num_pages = parseInt(data['num_pages']);
                    $scope.list_data[target].page_range = [];
                    $scope.setPageRange(target);
                    $scope[target] = data['results'];
                })
                .error(function (error) {
                    $scope.status = 'Unable to load related '+target+': ' + error.message;
                });
        }

    }
})(angular);