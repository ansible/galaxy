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

var ratingServices = angular.module('ratingServices', ['ngResource']);
 
ratingServices.factory('ratingFactory', ['$http','$cookies',
  function($http, $cookies){
    var dataFactory = {};

    $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;

    dataFactory.getRatings = function(page, results_per_page, sort_order, filter) { 
      var url = '/api/v1/ratings/?page=' + page + '&order_by=' + sort_order + '&page_size=' + results_per_page;
      if (filter && filter != '') {
        url += '&owner__username__contains=' + filter;
      }
      return $http.get(url);
    };
    dataFactory.getRating = function(id) {
      return $http.get('/api/v1/ratings/' + id);
    };
    dataFactory.getLatest = function(page, results_per_page) {
      return dataFactory.getRatings(page, results_per_page, '-created');
    };
    dataFactory.addRating = function(target, data) {
      return $http.put(target, data);
    };
    dataFactory.deleteRating = function(id) {
      var url = '/api/v1/ratings/'+id+'/'
      return $http.delete(url);
    }
    dataFactory.addVote = function(id, data, direction) {
      var url = '/api/v1/ratings/'+id+'/'+direction+'_votes/'
      return $http.post(url, data);
    }
    dataFactory.getMyRatingForRole = function(my_id, role_id) {
      var url = '/api/v1/ratings/?owner='+my_id+'&role='+role_id;
      return $http.get(url);
    };
    return dataFactory;
  }
]);
