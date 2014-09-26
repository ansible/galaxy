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

var storageServices = angular.module('storageServices', ['ngResource']);
 
storageServices.factory('storageFactory', [
  function () {
    var dataFactory = {};
    dataFactory.save_state = function(target, fields) { 
      var data = {};
      for (var fname in fields) {
         data[fname] = fields[fname];
      }
      localStorage[target] = JSON.stringify(data);
    };
    dataFactory.restore_state = function(target, default_fields) {
      try {
        var data = JSON.parse(localStorage[target]);
        for (var fname in default_fields) {
          if (typeof(data[fname]) == 'undefined') {
            data[fname] = default_fields[fname];
          }
        }
        return data;
      } catch(err) {
        return default_fields;
      }
    };
    return dataFactory;
  }
]);
