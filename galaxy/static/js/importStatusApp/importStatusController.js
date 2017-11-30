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

    var mod = angular.module('importStatusController', []);

    mod.controller('ImportStatusCtrl', [
        '$scope',
        '$log',
        '$window',
        '$interval',
        '$timeout',
        '$location',
        'currentUserService',
        'importService',
        'imports',
        _controller]);

    function _controller($scope, $log, $window, $interval, $timeout, $location, currentUserService, importService, imports) {
        $scope.imports = imports;
        $scope.user = currentUserService;
        $scope.checking = false;
        $scope.loading = false;
        $scope.searchText = '';
        $scope.page_title = 'My Imports';
        $scope.showDetail = _getDetail;
        $scope.reimportRole = _reimport;
        $scope.checkAddRole = _checkAddRole;
        
        var params = $location.search();
        if (params.github_repo) {
            $scope.searchText = params.github_repo
            $scope.selected_id = 0;
            imports.every(function(imp) {
                if (imp.github_user == params.github_user && imp.github_repo == params.github_repo) {
                    $scope.selected_id = imp.id;
                    $scope.selected_github_user = imp.github_user;
                    $scope.selected_github_repo = imp.github_repo;
                    return false;
                }
                return true;
            });
        } else {
            if (imports.length && !$scope.selected_id) {
                $scope.selected_id = imports[0].id;
                $scope.selected_github_user = imports[0].github_user;
                $scope.selected_github_repo = imports[0].github_repo;
            }
        }

        if ($scope.imports.length && $scope.selected_id) {
            $scope.loading = true;
            _showDetail($scope.selected_id);
        }

        var stop = $interval(_getImports, 5000);

        var lazy_resize = _.debounce(function() { 
            _resize();
        }, 500);

        $($window).resize(lazy_resize);
        _resize();

        $scope.$on('$destroy', function() {
            $interval.cancel(stop);
        });

        return;


        function _checkAddRole() {
            return !($scope.addRoleUsername && $scope.addRoleRepo);
        }

        function _showAddForm() {
            $scope.showAddRole = !$scope.showAddRole;
            $scope.addRoleUsername = null;
            $scope.addRoleRepo = null;
        
            if ($scope.showAddRole)
                $timeout(function() {
                    $('#add-role-username').focus();
                },500);
        }

        function _reimport(_github_user, _github_repo) {
            importService.imports.save({
                'github_user': _github_user,
                'github_repo': _github_repo,
            }).$promise.then(function(data) {
                $scope.selected_id = data.results[0].id;
                _getImports();
            });
        }

        function _getImports() {
            // reload the data
            $scope.checking = true;
            importService.imports.get({owner_id: currentUserService.id}).then(function(data) { 
                $scope.checking = false; 
                $scope.imports = data;

                // get the latest import id for the selected repo
                data.every(function(imp) {
                    if (imp.github_user === $scope.selected_github_user &&
                        imp.github_repo === $scope.selected_github_repo) {
                        $scope.selected_id = imp.id;
                        return false;
                    }
                    return true;
                });
                _showDetail($scope.selected_id);
            });
        }

        function _resize() {
            if ($($window).width() > 992) {
                var h = $($window).height() - 300 - $('#galaxy-copyright').height();
                h = (h < 300) ? 300 : h;
                $('#import-list-inner').css({ 'height': h + 'px' });
            } else {
                $('#import-list-inner').css({ 'height': '300px' });
            }

        }

        function _getDetail(_import_id) {
            if (!$scope.loading) {
                $scope.loading = true;
                $scope.selected_id = _import_id;
                $scope.imports.every(function(imp) {
                    if (imp.id === _import_id) {
                        $scope.selected_github_repo = imp.github_repo;
                        $scope.selected_github_user = imp.github_user;
                        return false;
                    }
                    return true;
                });
                _showDetail(_import_id);
            }
        }

        function _showDetail(_import_id) {
            if (!$scope.selected_id)
                return;

            importService.import.get({ import_id: _import_id }).$promise.then(function(data) {
                $scope.import_detail = data;

                //$scope.import_detail.travis_status_url = "https://travis-ci.org/ansible/tower-cli.svg?branch=master";
                //$scope.import_detail.travis_build_url = "https://travis-ci.org/ansible/tower-cli/builds/94920028";

                if ($scope.import_detail.state == 'PENDING') {
                     $scope.import_detail['last_run'] = "Waiting to start...";
                }
                else if ($scope.import_detail.state == 'RUNNING') {
                    $scope.import_detail['last_run'] = "Running...";
                }
                else if ($scope.import_detail.finished) {
                    var now = new Date();
                    var finished = new Date($scope.import_detail.finished);

                    var diff = (now.getTime() - finished.getTime()) / 1000;
                    var days = (diff >= 86400) ? Math.floor(diff / 86400) : 0;
                    var hours = (diff > 3600) ? Math.floor((diff  - (days * 86400)) / 3600) : 0;
                    var minutes = (diff > 60) ? Math.floor((diff - (days * 86400) - (hours * 3600)) / 60) : 0;
                    var seconds = Math.ceil(diff - (days * 86400) - (hours * 3600) - (minutes * 60));
                    var when = '';
                    if (days) {
                        when = 'Finished about ' + days + ' day' + ((days > 1) ? 's' : '') + ' ago';
                    } else if (hours) {
                        when = 'Finished about ' + hours + ' hour' + ((hours > 1) ? 's' : '') + ' ago'; 
                    } else if (minutes) {
                        when = 'Finished about ' + minutes + ' minute' + ((minutes > 1) ? 's' : '') + ' ago';
                    } else {
                        when = 'Finished about ' + seconds + ' second' + ((seconds > 1) ? 's' : '') + ' ago';
                    }
                    $scope.import_detail['last_run'] = when;
                } else {
                  $scope.import_detail['last_run'] = ''; 
                }
                $scope.loading = false;
            });
        }
    }

})(angular);
