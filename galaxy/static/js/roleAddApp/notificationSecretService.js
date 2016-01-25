/*
 * notificationSecretService.js
 */

'use strict';

(function(angular) {

    var mod = angular.module('notificationSecretService', []);

    mod.factory('notificationSecretService', ['$resource', 'getCSRFToken', _factory]);

    function _factory($resource, getCSRFToken) {
        var token = getCSRFToken();
        return $resource('/api/v1/notification_secrets/:id/', {'id': '@id'}, {
               'put': {method: 'PUT', isArray: false, headers: { "X-CSRFToken": token }},
              'save': {method: 'POST', headers: { "X-CSRFToken": token }},
            'delete': {method: 'DELETE', headers: { "X-CSRFToken": token }, isArray: false }
        });
    }

})(angular);