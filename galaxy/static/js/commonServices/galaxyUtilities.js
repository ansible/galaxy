/*
 * galaxyUtilities.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {
    var mod = angular.module('galaxyUtilities', [])
    
    mod.factory('Empty', [_Empty]);
    mod.factory('Range', [_Range]);
    mod.factory('Stars', [_Stars]);
    mod.factory('queryParams', [_queryParams]);
    mod.factory('fromQueryParams', [_fromQueryParams]);

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
            result.results_per_page = data.per_page;
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
            result.per_page = data.results_per_page;
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

})(angular);

