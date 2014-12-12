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

var meServices = angular.module('meServices', ['ngResource']);
 
meServices.factory('meFactory', ['$http','$q','storageFactory',
  function($http, $q, storageFactory) {
    var dataFactory = {};
    dataFactory.default_state = {
      'id': null,
      'authenticated': 0,
      'username': '',
      'timestamp': null
    };
    dataFactory.getMyCachedInfo = function() {
      return storageFactory.restore_state('my_info', dataFactory.default_state);
    };
    dataFactory.saveInfo = function(data) {
      var info = angular.copy(data);
      info.timestamp = new Date();
      storageFactory.save_state('my_info', info)
    };
    dataFactory.fetchMyInfo = function() {
      var url = '/api/v1/me/';
      return $http.get(url);
    };
    return dataFactory;
  }
]);

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

meServices.provider('MyInfo', MyInfoProviderFunction);
