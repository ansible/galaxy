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
    var mod = angular.module('galaxyUtilities', [])
    
    mod.factory('Empty', [_Empty]);
    mod.factory('Range', [_Range]);
    mod.factory('Stars', [_Stars]);
    mod.factory('queryParams', [_queryParams]);
    mod.factory('fromQueryParams', [_fromQueryParams]);
    mod.factory('getCSRFToken', [_getToken]);

    // Configure moment.js tresholds
    moment.relativeTimeRounding(Math.floor);
    moment.relativeTimeThreshold('s', 60);
    // NOTE(cutwater): Setting 'ss' treshhold before 's' overrides
    // it's value to 's' - 1
    moment.relativeTimeThreshold('ss', 0);
    moment.relativeTimeThreshold('m', 60);
    moment.relativeTimeThreshold('h', 24);
    moment.relativeTimeThreshold('d', 31);
    moment.relativeTimeThreshold('M', 12);

    mod.filter('timeFromNow', function () {
        return function (value) {
            return moment(value).fromNow();
        }
    });

    // check if a scalar is empty
    function _Empty() {
        return function(v) {
            return (v === undefined || v === null || v === '') ? true : false;
        };
    }


    // Create an array with x number of elements.
    // Then pass the array into ng-repeat to create a 'range' effect.
    function _Range() {
        return function (cnt, value) {
            var range = new Array();
            for (var i=0; i < cnt; i++)
                range.push({ id: i, value: value });
            return range;
        };
    }

 
    function _Stars() {
        return function (rating) {
            var stars = new Array();
            var value = parseFloat(rating);
            var floor = Math.floor(value);
            for (var i=0; i < floor; i++) {
                stars.push({ id: i, value: 'fa fa-star' });    
            }
            if (value % 1 > 0) {
                stars.push({ id: i, value: 'fa fa-star-half-o' });
            }
            for (var i=stars.length; i < 5; i++) {
                stars.push({ id: i, value: 'fa fa-star-o' });
            }
            return stars;
        };
    }


    function _fromQueryParams() {
        return function (data) {
            var result = {};
            result.list_filter = data.f;
            result.page = data.page;
            result.page_size = data.per_page;
            result.sort_order = data.sort_order;
            result.reverse = data.reverse;
            result.selected_categories = data.cats;
            result.platform = data.platform;
            result.release = data.release;
            return result;
        };
    }


    function _queryParams() {
        return function(data) {
            var result = {};
            result.page = data.page;
            result.per_page = data.page_size;
            result.sort_order = data.sort_order;
            if (data.list_filter)
                result.f = data.list_filter;
            if (data.platform)
                result.platform = data.platform;
            if (data.release)
                result.release = data.release;
            if (data.reverse)
                result.reverse = data.reverse;
            if (data.selected_categories)
                result.cats = data.selected_categories;
            return result;
        };
    }

    function _getToken() {
        return function() {
            // Get the CSRF token
            // https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
            var name = 'csrftoken';
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    }   

})(angular);

