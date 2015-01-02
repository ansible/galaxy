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

/* App Module */

var roleApp = angular.module('roleApp', [
  'ngRoute',
  'ngSanitize',
  'ngCookies',
  'ui.bootstrap',
  'ui.slider',
  'listControllers',
  'listDirectives',
  'meServices',
  'categoryServices',
  'ratingServices',
  'roleServices',
  'storageServices',
  'userServices',
  'relatedService',
  'Paginate'
]);

// FIXME: this should probably go in a utilities library
function getMyInfo($q, meFactory) {
  /*
  // caching stuff removed for now, since, after
  // a login/logout, the information is not refreshed.
  var now = new Date();
  var info = meFactory.getMyCachedInfo();
  if (info.timestamp) {
    try {
      var timestamp = new Date(info.timestamp);
      // cached info persists for 1 minutes
      if ((now - timestamp) < 60000) {
        return info;
      }
    } catch(err) {
      // ignore the error and fall through to fetch
    }
  }
  */

    var d = $q.defer();
    meFactory.fetchMyInfo()
        .success(function(data) {
            meFactory.saveInfo(data);
            d.resolve(data);
            })
        .error(function(err) {
            d.reject(err);
            });
    return d.promise;
}

roleApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/roles', {
          templateUrl: '/static/partials/role-list.html',
          controller: 'RoleListCtrl',
          reloadOnSearch: false,
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo]
              }
          }).
      when('/roles/category/:category_name', {
          templateUrl: '/static/partials/role-list.html',
          controller: 'RoleListCtrl',
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo]
              }
          }).
      when('/roles/sort/:sort_order', {
          templateUrl: '/static/partials/role-list.html',
          controller: 'RoleListCtrl',
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo], 
              }
          }).
      when('/roles/:role_id', {
          templateUrl: '/static/partials/role-detail.html',
          controller: 'RoleDetailCtrl',
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo]
              } 
          }).
      when('/users', {
          templateUrl: '/static/partials/user-list.html',
          controller: 'UserListCtrl',
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo]
              }
          }).
      when('/users/sort/:sort_order', {
          templateUrl: '/static/partials/user-list.html',
          controller: 'UserListCtrl',
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo]
              }
          }).
      when('/users/:user_id', {
          templateUrl: '/static/partials/user-detail.html',
          controller: 'UserDetailCtrl',
          resolve: {
              my_info: ['$q', 'meFactory', getMyInfo]
              }
          }).
      otherwise({
          redirectTo: '/roles'
          });
  }]);
