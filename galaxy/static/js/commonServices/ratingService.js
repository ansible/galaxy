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
    
    var mod = angular.module('ratingService', ['ngResource']);
     
    mod.factory('ratingFactory', ['$http','$cookies', _factory]);

    function _factory($http, $cookies){

        $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
        
        return {
            getRatings: _getRating,
            getRating: _getRating,
            getLatest: _getLatest,
            addRating: _addRating,
            deleteRating: _deleteRating,
            addVote: _addVote,
            getMyRatingForRole: _getMyRatingForRole
        };

        function _getRatings(page, results_per_page, sort_order, filter) { 
            var url = '/api/v1/ratings/?page=' + page + '&order_by=' + sort_order + '&page_size=' + results_per_page;
            if (filter && filter != '') {
                url += '&owner__username__contains=' + filter;
            }
            return $http.get(url);
        }
        
        function _getRating(id) {
            return $http.get('/api/v1/ratings/' + id);
        }

        function _getLatest(page, results_per_page) {
            return dataFactory.getRatings(page, results_per_page, '-created');
        }

        function _addRating(target, data) {
            return $http.put(target, data);
        }

        function _deleteRating(id) {
            var url = '/api/v1/ratings/'+id+'/'
            return $http.delete(url);
        }
        
        function _addVote(id, data, direction) {
            var url = '/api/v1/ratings/'+id+'/'+direction+'_votes/'
            return $http.post(url, data);
        }
        
        function _getMyRatingForRole(my_id, role_id) {
            var url = '/api/v1/ratings/?owner='+my_id+'&role='+role_id;
            return $http.get(url);
        }
    }
  
})(angular);
