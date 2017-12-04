/* (c) 2012-2017, Ansible by Red Hat
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

    var mod = angular.module('userStarredController', []);

    mod.controller('UserStarredCtrl', [
        '$scope',
        '$log',
        '$window',
        '$interval',
        '$timeout',
        '$location',
        'currentUserService',
        'userStarredService',
        'stars',
        _controller]);

    function _controller($scope, $log, $window, $interval, $timeout, $location, currentUserService, userStarredService, stars) {
        $scope.stars = stars;
        $scope.user = currentUserService;
        $scope.checking = false;
        $scope.loading = false;
        $scope.searchText = '';
        $scope.page_title = 'My Stars';
    }

})(angular);
