/*
 * listApp.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
  
    var roleApp = angular.module('listApp', [
        'ngRoute',
        'ngSanitize',
        'ngCookies',
        'ui.bootstrap',
        'meService',
        'categoryService',
        'ratingService',
        'roleService',
        'storageService',
        'userService',
        'relatedService',
        'roleListController',
        'roleDetailController',
        'userListController',
        'userDetailController',
        'paginateService',
        'searchService',
        'platformService',
        'galaxyDirectives',
        'galaxyUtilities'
    ]);

    roleApp.config(['$routeProvider', _routes]);

    function _routes($routeProvider) {
      $routeProvider.
          when('/roles', {
              templateUrl: '/static/partials/role-list.html',
              controller: 'RoleListCtrl',
              reloadOnSearch: false,
              resolve: {
                  my_info: ['$q', 'meFactory', _getMyInfo]
              }
          }).
          when('/roles/:role_id', {
              templateUrl: '/static/partials/role-detail.html',
              controller: 'RoleDetailCtrl',
              resolve: {
                  my_info: ['$q', 'meFactory', _getMyInfo]
              }
          }).
          when('/users', {
              templateUrl: '/static/partials/user-list.html',
              controller: 'UserListCtrl',
              reloadOnSearch: false,
              resolve: {
                  my_info: ['$q', 'meFactory', _getMyInfo]
              }
          }).
          when('/users/:user_id', {
              templateUrl: '/static/partials/user-detail.html',
              controller: 'UserDetailCtrl',
              resolve: {
                  my_info: ['$q', 'meFactory', _getMyInfo]
              }
          }).
          otherwise({
              redirectTo: '/roles'
          });
    }

    function _getMyInfo($q, meFactory) {
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

})(angular);
