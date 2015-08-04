/*
# (c) 2015 Ansible, Inc. <support@ansible.com>
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

(function(angular) {

    angular.module('platformService', ['ngResource'])
        .factory('platformService', ['$resource', '$q', _factory]);

    function _factory($resource, $q) {
        var res = $resource('/api/v1/platforms');
        var platforms = [];
        return {
            get: _get
        };

        function _get() {
            var deferred = $q.defer();
            if (platforms.length == 0) {
               // load for the first time
               return _loadPlatforms();
            }
            deferred.resolve(platforms);
            return deferred.promise;
        }

        function _loadPlatforms() {
            return res.get().$promise.then(function(data){
                var obj = {};
                platforms = [];
                angular.forEach(data, function(platform) {
                    obj[platform.name] = platform.name;
                });
                angular.forEach(obj, function(val) {
                    platforms.push({
                        name: val,
                        value: val
                    });
                });
                return platforms;
            });
        }
    }

})(angular);
