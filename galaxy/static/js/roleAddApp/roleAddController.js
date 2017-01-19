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
    
    var mod = angular.module('roleAddController', []);

    mod.controller('RoleAddCtrl', [
        '$scope',
        '$interval',
        '$timeout',
        '$analytics',
        '$q',
        'githubRepoService',
        'currentUserService',
        'importService',
        'roleService',
        'repositories',
        'notificationSecretService',
        _controller
    ]);

    function _controller(
        $scope,
        $interval,
        $timeout,
        $analytics,
        $q,
        githubRepoService,
        currentUserService,
        importService,
        roleService,
        repositories,
        notificationSecretService) {

        
        $scope.page_title = 'My Roles';
        $scope.loading = true;
        $scope.repositories = repositories;
        $scope.username = currentUserService.username;
        $scope.auth_orgs_url = currentUserService.auth_orgs_url;
        $scope.toggleRepository = _toggleRepository;
        $scope.refreshing = false;
        $scope.refreshRepos = _refresh;
        $scope.showIntegrations = _showIntegrations;
        $scope.cancelIntegrations = _cancelIntegrations;
        $scope.revealGithub = _revealGithub;
        $scope.revealTravis = _revealTravis;
        $scope.clearTravis = _clearTravis;
        $scope.clearGithub = _clearGithub;
        $scope.updateSettings = _updateSettings;
        $scope.reimport = _importRepository;
        $scope.github_auth = true;
        $scope.validateName = _validateName;
        $scope.deleteCancel = _deleteCancel;
        $scope.delete = _delete;


        if (!(currentUserService.authenticated && currentUserService.connected_to_github)) {
            $scope.github_auth = false;
            $scope.loading = false;
            return;
        }
        
        if (currentUserService.cache_refreshed) {
            $scope.loading = false;
            _setup();
        } else {
            _waitForRefresh();
        }

        return;

        
        function _waitForRefresh() {
            var stop = $interval(function() {
                currentUserService.update().then(function(userData) {
                    if (userData.cache_refreshed) {
                        _kill();
                    }
                });
            }, 5000);

            function _kill() {
                $interval.cancel(stop);
                if ($scope.repositories.length == 0) {
                    githubRepoService.get().$promise.then(function(response) {
                        $scope.loading = false;
                        $scope.repositories = response.results;
                        _setup();
                    });
                } else {
                    $scope.loading = false;
                    _setup();
                }
            }
        }

        function _setup() {
            $scope.repositories.forEach(function(repo) {
                repo.github_secret_type = "password";
                repo.travis_token_type = "password";
                repo.name_pattern_error = false;
                repo.show_enable_failed = false;
                repo.show_enable_failed_msg = '';
                if (repo.summary_fields) {
                    repo.summary_fields.notification_secrets.forEach(function(secret) {
                        if (secret.source == 'travis') {
                            repo.travis_id = secret.id;
                            repo.travis_token = secret.secret;
                        } else {
                            repo.github_id = secret.id;
                            repo.github_secret = secret.secret;
                        }
                    });
                }
                if (repo.summary_fields && repo.summary_fields.roles.length) {
                    repo.role_id = repo.summary_fields.roles[0].id;
                    repo.role_name = repo.summary_fields.roles[0].name;
                    repo.role_namespace = repo.summary_fields.roles[0].namespace;
                    if (repo.summary_fields.roles[0].last_import['state']) {
                        repo.state = repo.summary_fields.roles[0].last_import.state;
                    } else {
                        repo.state = repo.summary_fields.roles[0].last_import.state = null;
                    }
                    repo.master_role_name = repo.role_name;
                } else {
                    var new_name;
                    if (repo.github_repo === 'ansible') {
                        new_name = repo.github_repo;
                    } else {
                        repo.github_repo.replace(/^(ansible[-_+.]*)*(role[-_+.]*)*/g, function(match, p1, p2, offset, str) {
                            var result = str;
                            if (p1) {
                                result = result.replace(new RegExp(p1,'g'), '');
                            }
                            if (p2) {
                                result = result.replace(new RegExp(p2,'g'), '');
                            }
                            result = result.replace(/^-/,'');
                            new_name = result;
                        });
                        if (!new_name) {
                            new_name = repo.github_repo;
                        }
                    }
                    repo.role_namespace = repo.github_user
                    repo.role_name = new_name;
                    repo.master_role_name = repo.role_name;
                }
            });
        }

        function _resetRepo(_repo) {
            // Restore repo values
            _repo.role_name = _repo.master_role_name
            _repo.travis_id = $scope.master.travis_id;
            _repo.travis_token = $scope.master.travis_token;
            _repo.github_id = $scope.master.github_id;
            _repo.github_secret = $scope.github_secret;
            _repo.name_pattern_error = false;
        }

        function _showIntegrations(_repo) {
            _repo.show_integrations = !_repo.show_integrations; 
            _repo.github_secret_type = "password";
            _repo.travis_token_type = "password";
            if (_repo.show_integrations) {
                // reveal the form. keep a copy in case user clicks cancel.
                $scope.master = {
                    travis_id: _repo.travis_id,
                    travis_token: _repo.travis_token,
                    github_id: _repo.github_id,
                    github_secret: _repo.github_secret
                };
            } else {
                // hide the form
                _resetRepo(_repo);
            }
        }

        function _cancelIntegrations(_repo) {
            _resetRepo(_repo);
            _repo.show_integrations = !_repo.show_integrations;
        }

        function _revealGithub(_repo) {
            _repo.github_secret_type = (_repo.github_secret_type == 'password') ? 'text' : 'password';
        }

        function _revealTravis(_repo) {
            _repo.travis_token_type = (_repo.travis_token_type == 'password') ? 'text' : 'password';
        }

        function _clearTravis(_repo) {
            _repo.travis_token = null;
        }

        function _clearGithub(_repo) {
            _repo.github_secret = null;
        }

        function _updateSettings(_repo) {
            _validateName(_repo);
            if (!_repo.name_pattern_error) {
                $scope.name_pattern_error = false;
                _repo.show_integrations = false;
                _updateRoleName(_repo).then(function() {
                    _updateSecrets(_repo);
                });
            }
        }

        function _updateRoleName(_repo) {
            var deferred = $q.defer();
            if (_repo.master_role_name !== _repo.role_name) {
                _repo.is_enabled = true;
                _repo.state = 'PENDING';
                _repo.master_role_name = _repo.role_name;
                importService.imports.save({
                    'github_user': _repo.github_user,
                    'github_repo': _repo.github_repo,
                    'alternate_role_name': _repo.role_name
                }).$promise.then(function(data) {
                    _checkStatus(data, deferred);
                });
            } else {
                $timeout(function() {
                    deferred.resolve();
                }, 300);
            }
            return deferred.promise;
        }

        function _updateSecrets(_repo) {
            // deleted secret
            if (_repo.travis_id && !_repo.travis_token) {
                $analytics.eventTrack('remove_travis', {
                    category: _repo.github_user + '/' + _repo.github_repo
                });
                notificationSecretService.delete({id: _repo.travis_id}).$promise.then(function(repsonse) {
                    _repo.travis_id = null;
                });
            }
            // changed secret
            if (_repo.travis_id && _repo.travis_token && !/^\*{6}/.test(_repo.travis_token)) {
                $analytics.eventTrack('change_travis', {
                    category: _repo.github_user + '/' + _repo.github_repo
                });
                notificationSecretService.put({
                    id: _repo.travis_id,
                    source: 'travis',
                    github_user: _repo.github_user,
                    github_repo: _repo.github_repo,
                    secret: _repo.travis_token
                }).$promise.then(function(response) {
                    _repo.travis_token = response.secret;
                });
            }
            // new secret
            if (!_repo.travis_id && _repo.travis_token && !/^\*{6}/.test(_repo.travis_token)) {
                $analytics.eventTrack('add_travis', {
                    category: _repo.github_user + '/' + _repo.github_repo
                });
                notificationSecretService.save({
                    source: 'travis',
                    github_user: _repo.github_user,
                    github_repo: _repo.github_repo,
                    secret: _repo.travis_token
                }).$promise.then(function(response) {
                    _repo.travis_id = response.id;
                    _repo.travis_token = response.secret;
                });
            }
        }
        
        function _refresh() {
            if ($scope.loading || $scope.refreshing) {
                return 
            }
            $scope.refreshing = true;
            githubRepoService.refresh().$promise.then(function(response) {
                $timeout(function() {
                    $scope.refreshing = false;
                    $scope.$apply();
                },1000);
                $scope.repositories = response;
                _setup();
            });
        }

        function _importRepository(_repo) {
            if (_repo.is_enabled) {
                _repo.state = 'PENDING';
                importService.imports.save({
                    'github_user': _repo.github_user,
                    'github_repo': _repo.github_repo,
                    'alternate_role_name': _repo.role_name
                }).$promise.then(_checkStatus, function(response) {
                    // handle an error
                    _repo.show_enable_failed = true;
                    var msg = ''
                    if (response.config && response.config.url) {
                        msg = 'Request to ' + response.config.url + ' resulted in ';
                    }
                    _repo.enable_failed_msg = msg + response.status + ' - ' + response.statusText;
                    _repo.is_enabled = false;
                });
            }
        }

        function _toggleRepository(_repo) {
            if (_repo.show_integrations)
                _cancelIntegrations(_repo);
            if (_repo.show_delete_warning)
                _deleteCancel(_repo);
            _repo.show_delete_failed=false;
            _repo.show_enable_failed=false;

            if (_repo.is_enabled) {
                _importRepository(_repo);
            } else {
                _repo.show_delete_warning = true;
            }
        }

        function _delete(_repo) {
            roleService.delete({
                'github_user': _repo.github_user,
                'github_repo': _repo.github_repo
            }).$promise.then(function(response) {
                $scope.repositories.forEach(function(repo) {
                    response.deleted_roles.forEach(function(deleted) {
                        if (deleted.github_user === repo.github_user && deleted.github_repo === repo.github_repo) {
                            repo.state = null;
                            repo.show_delete_warning = false;
                        }
                    });
                });
            }, function(error) {
                /* An error occurred. Likely the repo was renamed or deleted on the GitHub side */
                $scope.repositories.forEach(function(repo) {
                    repo.show_delete_warning = false;
                    if (_repo.github_user === repo.github_user && _repo.github_repo === repo.github_repo) {
                        repo.state = null;
                        repo.show_delete_failed = true;
                    }
                });
            });
        }

        function _deleteCancel(_repo) {
            _repo.show_delete_warning = false;
            _repo.is_enabled = true;
        }

        function _checkStatus(response, deferred) {
            var stop = $interval(function(_id) {
                importService.imports.query({ id: _id}).$promise.then(function(response) {
                    $scope.repositories.every(function(repo) {
                        if (repo.github_user == response.results[0].github_user && 
                            repo.github_repo === response.results[0].github_repo) {
                            repo.state = response.results[0].state;
                            repo.role_id = response.results[0].role;
                            return false;
                        }
                        return true;
                    });
                    if (response.results[0].state == 'SUCCESS' || response.results[0].state == 'FAILED') {
                        _kill();
                    }
                });
            }, 5000, 0, false, response.results[0].id)

            function _kill() {
                $interval.cancel(stop);
                if (deferred) {
                    deferred.resolve();
                }
            }
        }

        function _validateName(_repo) {
            if (/^[A-Za-z0-9\-_]+$/.test(_repo.role_name)) {
                _repo.name_pattern_error = false;
            } else {
                _repo.name_pattern_error = true;
            }
        }
    }

})(angular);
 

