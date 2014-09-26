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

angular.module('Utilities', [])
    
    // check if a scalar is empty
    .factory('Empty', [ function() {
    return function(v) {
        return (v === undefined || v === null || v === '') ? true : false;
        }
        }])


    // Create an array with x number of elements.
    // Then pass the array into ng-repeat to create a 'range' effect.
    .factory('Range', [ function() {
    return function (cnt, value) {
        var range = new Array();
        for (var i=0; i < cnt; i++)
            range.push({ id: i, value: value });
        return range;
        }
        }])

    .factory('Stars', [ function() {
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
        }
        }])

