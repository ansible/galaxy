/*
 * headerService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {

    var mod = angular.module('headerService', []);

    mod.factory('headerService',[ _factory]);

    function _factory() {
        var title = '';
        return {
            setTitle: _setTitle,
            getTitle: _getTitle
        };


        function _setTitle(_title) {
            title = _title;
        }

        function _getTitle() {
            return title;
        }
    }

})(angular);
