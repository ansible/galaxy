/* (c) 2012-2016, Ansible by Red Hat
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

    var mod = angular.module('storageService', []);

    function defineStorageService(adapter) {
        return {
            save_state: _saveState,
            restore_state: _restoreState
        };

        function _saveState(data) {
            adapter.save(data);
        }

        function _restoreState(default_fields) {
            try {
                var data = adapter.restore();
                for (var fname in default_fields) {
                    if (typeof(data[fname]) == 'undefined') {
                        data[fname] = default_fields[fname];
                    }
                }
                return data;
            } catch(err) {
                return default_fields;
            }
        }
    }

    mod.factory('queryStorageFactory', ['$location', _queryStorageFactory]);

    function _queryStorageFactory($location) {
        return defineStorageService({
            save: function(data) {
                return $location.search(JSON.parse(JSON.stringify(data)));
            },
            restore: function() {
                return $location.search();
            }
        });
    }

    mod.factory('storageFactory', [ _storageFactory]);

    function _storageFactory() {
        return defineStorageService({
            save: function(target, data) {
                localStorage[target] = JSON.stringify(data);
                return localStorage[target];
            },
            restore: function(target) {
                return JSON.parse(localStorage[target]);
            }
        });
    }

})(angular);
