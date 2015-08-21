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

(function(angular) {

    var mod = angular.module('storageServices', []);

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
