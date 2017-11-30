/* (c) 2012-2018, Ansible by Red Hat
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
