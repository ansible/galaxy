/*
 * headerController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {

    var mod = angular.module('headerController', ['headerService']);

    mod.controller('HeaderCtrl', ['$scope', '$log', 'headerService', _controller]);

    function _controller($scope, $log, headerService) {
        $scope.getTitle = _getTitle;
        
        return;


        function _getTitle() {
            return headerService.getTitle();
        }
    }

})(angular);
