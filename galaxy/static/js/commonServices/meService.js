/*
 * meService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('meService', ['ngResource']);
 
    mod.factory('meFactory', ['$http','$q','storageFactory', _factory]);

    function _factory($http, $q, storageFactory) {
        return {
            default_state: _defaultState,
            getMyCachedInfo: _getMyCachedInfo,
            saveInfo: _saveInfo,
            fetchMyInfo: _fetchMyInfo
        };

        var _defaultState = {
            'id': null,
            'authenticated': 0,
            'username': '',
            'timestamp': null
        };
        
        function _getMyCachedInfo() {
            return storageFactory.restore_state('my_info', _defaultState);
        }

        function _saveInfo(data) {
            var info = angular.copy(data);
            info.timestamp = new Date();
            storageFactory.save_state('my_info', info)
        }

        function _fetchMyInfo() {
            var url = '/api/v1/me/';
            return $http.get(url);
        }
    }


    function MyInfoProviderFunction() {
        var url = '/api/v1/me/';
        this.$get = ['$q', 'meFactory', function($q, meFactory) {
            var d = $q.defer();
            meFactory.fetchMyInfo()
                .success(function(data) {
                    d.resolve(data);
                })
                .error(function(err) {
                    d.reject(err);
                });
            return d.promise;
        }];
    }

    mod.provider('MyInfo', MyInfoProviderFunction);

})(angular);
