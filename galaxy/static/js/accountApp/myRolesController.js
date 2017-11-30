/* (c) 2012-2018, Ansible by Red Hat
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
  
    var mod = angular.module('myRolesController', []);

    mod.controller('MyRolesCtrl', [
        '$scope',
        '$location',
        '$timeout',
        'meFactory',
        'my_info',
        _controller
    ]);
    
    function _controller(
        $scope,
        $location,
        $timeout,
        meFactory,
        my_info) {

        $scope.my_info = my_info;
        $scope.polling = false;

        $scope.update_data = function(data) {
            for (var i in data.summary_fields.roles) {
                var new_obj = data.summary_fields.roles[i];
                for (var j in $scope.my_info.summary_fields.roles) {
                    var old_obj = $scope.my_info.summary_fields.roles[i];
                    if (old_obj.id == new_obj.id) {
                        if (old_obj.import.state != new_obj.import.state) {
                            old_obj.import.state = new_obj.import.state;
                            old_obj.import.status_message = new_obj.import.status_message;
                        }
                        break;
                    }
                }
            }
        };

        $scope.set_polling = function() {
            // to prevent unneccesary continual polling of the API,
            // we check to make sure there is at least one role in 
            // the list who's state may be changing
            for (var idx in $scope.my_info.summary_fields.roles) {
                var role = $scope.my_info.summary_fields.roles[idx];
                if (role.import.state != 'SUCCESS' && role.import.state != 'FAILURE') {
                    $scope.polling = true;
                    return;
                }
            }
            $scope.polling = false;
        };

        $scope.refresh = function() {
            meFactory.fetchMyInfo()
              .success(function(data) {
                  $scope.update_data(data);
              })
              .error(function(err) {
              
              });
        };

        $scope.poll = function() {
            $scope.set_polling();
            if ($scope.polling) {
                $timeout(function() {
                  $scope.refresh();
                  $scope.poll();
                }, 1000);
            }
        };

        $scope.poll();
    }

})(angular);

