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


var showcaseServices = angular.module('showcaseServices', []);
 
showcaseServices.factory('showcaseFactory', function() {
    var dataFactory = {};
    dataFactory.getRoles = function() {
        return {};
    };

    return dataFactory;
        // getRoles: function() {
        //     return [{
        //             name: 'arista',
        //             href: '/list#/roles?f=arista'
        //         }, {
        //             name: 'cumulus'
        //         }, {
        //             name: 'django'
        //         }, {
        //             name: 'docker'
        //         }, {
        //             name: 'elk-stack'
        //         }, {
        //             name: 'hadoop'
        //         }, {
        //             name: 'jenkins'
        //         }, {
        //             name: 'jira'
        //         }, {
        //             name: 'juniper'
        //         }, {
        //             name: 'mongodb'
        //         }, {
        //             name: 'mysql'
        //         }, {
        //             name: 'new-relic'
        //         }, {
        //             name: 'nodejs'
        //         }, {
        //             name: 'postgres'
        //         }, {
        //             name: 'rails'
        //         }, {
        //             name: 'redis'
        //         }, {
        //             name: 'tomcat'
        //         }, {
        //             name: 'wordpress'
        //         }
        //     ];
        // }
    // };
});
