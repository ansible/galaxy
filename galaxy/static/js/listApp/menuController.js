/*
 * roleListController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {

    var mod = angular.module('menuController', ['ngResource']);

    mod.controller('MenuCtrl', ['$scope', '$log', '$location', '$window', _controller]);

    function _controller($scope, $log, $location, $window) {
        $scope.redirectToSignin = _redirectToSignin;

        function _redirectToSignin() {
            var new_path = '/accounts/login/?next=' + encodeURIComponent('/list#' + $location.url());
            $log.debug('Set next to: ' + new_path);
            $window.location = new_path;
        }
    }


})(angular);