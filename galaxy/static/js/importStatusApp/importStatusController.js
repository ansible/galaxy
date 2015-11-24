/*
 * headerController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
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
        $scope.showAddForm = _showAddForm;

        var params = $location.search();
        if (Object.keys(params).length > 0) {
            imports.every(function(imp) {
                if (imp.github_user == params.github_user && imp.github_repo == params.github_repo) {
                    $scope.selected_id = imp.id;
                    return false;
                }
                return true;
            });
        }

        if (imports.length && !$scope.selected_id) {
            $scope.selected_id = imports[0].id;
        }

        if ($scope.imports.length) {
            $scope.loading = true;
            _showDetail($scope.selected_id);
        }

        $interval(_getImports, 5000);

        var lazy_resize = _.debounce(function() { 
            _resize();
        }, 500);

        $($window).resize(lazy_resize);
        _resize();

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

        function _reimport(_github_user, _github_repo, _github_branch) {
            importService.imports.save({
                'github_user': _github_user,
                'github_repo': _github_repo,
                'github_reference': _github_branch
            }).$promise.then(function(data) {
                console.log('selected_id: ' + $scope.selected_id);
                $scope.selected_id = data.results[0].id;
            });
        }

        function _getImports() {
            // reload the data
            $scope.checking = true;
            importService.imports.get({owner_id: currentUserService.id}).then(function(data) { 
                $scope.checking = false; 
                $scope.imports = data;
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
            if (!$scope.showAddRole) {
                $scope.loading = true;
                $scope.selected_id = _import_id;
                _showDetail(_import_id);
            }
        }

        function _showDetail(_import_id) {
            importService.import.get({ import_id: _import_id }).$promise.then(function(data) {
                $scope.import_detail = data;

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
                        when = 'Finished about ' + minutes + ' minutes' + ((minutes > 1) ? 's' : '') + ' ago';
                    } else {
                        when = 'Finished about ' + seconds + ' second' + ((seconds > 1) ? 's' : '') + ' ago';
                    }
                    $scope.import_detail['last_run'] = when;
                } else {
                  $scope.import_detail['last_run'] = ''; 
                }

                $scope.loading = false;
                _getRole($scope.import_detail.role);
            });
        }

        function _getRole(_role_id) {
            importService.role.get({ role_id: _role_id}).$promise.then(function(data) {
                $scope.role = data;
            });
        }
    }

})(angular);
