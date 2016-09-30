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

    var mod = angular.module('importService', []);
    
    mod.factory('importService', ['$analytics', '$resource', 'getCSRFToken', _factory]);

    function _factory($analytics, $resource, getCSRFToken) {

        var icons = {
            'FAILED': 'fa fa-exclamation-circle',
            'SUCCESS': 'fa fa-circle',
            'PENDING': 'fa fa-circle-o',
            'RUNNING': 'fa fa-spinner fa-pulse'
        };
        var date_labels = {
            'FAILED': 'Finished',
            'SUCCESS': 'Finished',
            'PENDING': 'Created',
            'RUNNING': 'Started'
        }

        return { 
            imports: {
                get: function(params) {
                    return $resource('/api/v1/imports/latest/',{ owner_id:'@id', page_size: 1000}).get(params).$promise.then(function(data) {
                        data.results.forEach(function(result) {
                            result.status_icon = icons[result.summary_fields.details.state];
                            result.date_label = date_labels[result.summary_fields.details.state];
                        });
                        return data.results;
                    });
                },
                save: function(params) {
                    var token = getCSRFToken();
                    var event_track = {
                        category: params.github_user + '/' + params.github_repo
                    };
                    $analytics.eventTrack('import', event_track);
                    return $resource('/api/v1/imports/',{}, {
                        'save': { 'method': 'POST', headers: { "X-CSRFToken": token }}
                    }).save(params);
                },
                query: function(params) {
                    return $resource('/api/v1/imports/').get(params);
                }
            },

            import: $resource('/api/v1/imports/:import_id/', { import_id: '@id' }),
            role:   $resource('/api/v1/roles/:role_id/', { role_id: '@id' })
        };
    }

})(angular);
