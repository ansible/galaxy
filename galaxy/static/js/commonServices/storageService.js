/*
 * storageService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('storageService', []);

    function defineStorageService(adapter) {
        return {
            save_state: _saveState,
            restore_state: _restoreState
        };

        function _saveState(target, fields) {
            var data = {};
            for (var fname in fields) {
                data[fname] = fields[fname];
            }
            adapter.save(target, data);
        }

        function _restoreState(target, default_fields) {
            try {
                var data = adapter.restore(target);
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
            save: function(key, data) {
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
