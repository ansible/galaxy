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

/* Directives */

var listDirectives = angular.module('listDirectives', []);

listDirectives.directive('ratingForm', function() {
    return {
        restrict: 'EA',
        templateUrl: '/static/partials/rating-form.html',
        transclude: true,
        scope: {
            role: '='
        },
        controller: ['$scope', '$q', 'ratingFactory', 'meFactory', function($scope, $q, ratingFactory, meFactory) {
            if (angular.isUndefined($scope.role)) {
                return;
            }

            var loadMyRating = function(values) {
                return ratingFactory.
                    getMyRatingForRole(values[0].id, values[1].id);
            };

            var myInfo = $q.when(meFactory.getMyCachedInfo())
            myInfo = myInfo.then(function(myInfo) {
                    $scope.my_info = myInfo;
                    return myInfo;
                });

            var currentRole = $q.when($scope.role);

            function resolveRatingData(response) {
                var data = response.data;
                if (data.count == 0) {
                    return null;
                }

                // it should never be > 1, but we only
                // care the first result anyway
                var res = angular.copy(data['results'][0]);
                var rating = {
                    'id': res.id,
                    'reliability': parseInt(res.reliability),
                    'documentation': parseInt(res.documentation),
                    'code_quality': parseInt(res.code_quality),
                    'wow_factor': parseInt(res.wow_factor),
                    'comment': res.comment
                }
                return rating;
            }

            function applyRatingToScope(rating) {
                if (rating) {
                    $scope.rating = rating;
                }
                else {
                    $scope.rating = {
                        'reliability': 0,
                        'documentation': 0,
                        'code_quality': 0,
                        'wow_factor': 0,
                        'comment': '',
                        }
                }
            }

            $q.all([myInfo, currentRole]).
                then(loadMyRating).
                then(resolveRatingData).
                then(applyRatingToScope);


            $scope.alerts = [];

            $scope.closeAlert = function(index) {
                $scope.alerts.splice(index, 1);
                };

            $scope.ok = function () {
                if ($scope.rating.reliability == 0 ||
                    $scope.rating.documentation == 0 ||
                    $scope.rating.code_quality == 0 ||
                    $scope.rating.wow_factor == 0 ) {
                        $scope.alerts = [{type: 'danger','msg':'You must choose a rating for each category'}]
                        return;
                    }
                var post_data = {
                    'pk': $scope.role.id,
                    }
                angular.extend(post_data, $scope.rating);
                ratingFactory.addRating(
                    $scope.role.related.ratings,
                    post_data
                    )
                    .error(function(data, status) {
                        var msg = '';
                        if (status == 403) {
                            msg = 'You do not have permission to add a rating to this role.';
                        } else if(status == 409) {
                            msg = 'You appear to have already rated this role. If your rating is not visible, it may mean that an administrator has removed it for violating our terms of service. If you believe this was done in error, please contact us.';
                        } else {
                            msg = 'An unknown error occurred while trying to add your rating. Please wait a while and try again.';
                        }
                        $scope.alerts = [{type: 'error','msg':msg}]
                        });
                };

            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
                };
        }],
        link: function() {
        }
    };
    //     };

});

listDirectives.directive('ratingStars', function() {
    return {
    // 4.5 -> [1,1,1,.5,0]
        restrict: 'E',
        scope: {
            rating: '@'
        },
        link: function(element, attrs, scope) {
            console.log('ratingStars: ', scope);
            console.log('rating: ', scope.rating);
            var roundedRating = Math.floor(scope.rating);
            var starsPlaceholder = new Array(roundedRating);
            console.log(starsPlaceholder.length);
        }
    };
});
