/*
 * platformService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    angular.module('platformService', ['ngResource'])
        .factory('platformService', ['$resource', '$q', _factory]);

    function _factory($resource, $q) {
        var res = $resource('/api/v1/platforms/');
        var platforms = [];
        var releases = {};
        return {
            getPlatforms: _getPlatforms,
            getReleases: _getReleases
        };

        function _getPlatforms() {
            var deferred = $q.defer();
            if (platforms.length == 0) {
               // load for the first time
               return _loadPlatforms();
            }
            deferred.resolve(platforms);
            return deferred.promise;
        }

        function _loadPlatforms() {
            return res.query().$promise.then(function(data){
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

        function _getReleases(_platform) {
            var deferred = $q.defer();
            if (!releases[_platform]) {
               // load for the first time
               return _loadReleases(_platform);
            }
            deferred.resolve(releases[_platform]);
            return deferred.promise;
        }

        function _loadReleases(_platform) {
            return res.query({ name: _platform }).$promise.then(function(data) {
                releases[_platform] = [];
                angular.forEach(data, function(release) {
                    releases[_platform].push({
                        name: release.release,
                        value: release.release
                    });
                });
                return releases[_platform];
            });
        }
    }

})(angular);
