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

    var mod = angular.module('githubClickService', ['currentUserService', 'githubRepoService']);

    mod.factory('githubClickService', ['$analytics', 'currentUserService', 'githubRepoService', _factory]);

    function _factory($analytics, currentUserService, githubRepoService) {

        return {
            subscribe: _subscribe,
            unsubscribe: _unsubscribe,
            star: _star,
            unstar: _unstar
        };

        function _analytics(event, _role) {
            $analytics.eventTrack(event, {
                category: _role.username + '.' + _role.name,
                label: _role.github_user + '/' + _role.github_repo
            });
        }

        function _subscribe(_role) {
            // Subscribe the user to the role repo
            if (currentUserService.authenticated && currentUserService.connected_to_github) {
                _role.subscribing = true;
                _analytics('watch', _role);
                githubRepoService.subscribe({
                    github_user: _role.github_user,
                    github_repo: _role.github_repo
                }).$promise.then(function() {
                    _role.watchers_count++;
                    _role.user_is_subscriber = true;
                    _role.subscribing = false;
                    currentUserService.update();
                });
            }
        }

        function _unsubscribe(_role) {
            // Find the user's subscription to the role repo and delete it
            if (currentUserService.authenticated && currentUserService.connected_to_github) {
                _role.subscribing = true;
                _analytics('unwatch', _role);
                var id;
                currentUserService.subscriptions.every(function(sub) {
                    if (sub.github_user == _role.github_user && sub.github_repo == _role.github_repo) {
                        id = sub.id;
                        return false;
                    }
                    return true;
                });
                if (id) {
                    githubRepoService.unsubscribe({
                        id: id
                    }).$promise.then(function() {
                        _role.watchers_count--;
                        _role.user_is_subscriber = false;
                        _role.subscribing = false;
                        currentUserService.update();
                    });
                } else {
                    _role.subscribing = false;
                }
            }
        }

        function _star(_role) {
            // Subscribe the user to the role repo
            if (currentUserService.authenticated && currentUserService.connected_to_github) {
                _role.starring = true;
                _analytics('star', _role);
                githubRepoService.star({
                    github_user: _role.github_user,
                    github_repo: _role.github_repo
                }).$promise.then(function() {
                    _role.stargazers_count++;
                    _role.user_is_stargazer = true;
                    _role.starring = false;
                    currentUserService.update();
                });
            }
        }

        function _unstar(_role) {
            // Find the user's subscription to the role repo and delete it
            if (currentUserService.authenticated && currentUserService.connected_to_github) {
                _role.starring = true;
                _analytics('unstar', _role);
                var id;
                currentUserService.starred.every(function(star) {
                    if (star.github_user == _role.github_user && star.github_repo == _role.github_repo) {
                        id = star.id;
                        return false;
                    }
                    return true;
                });
                if (id) {
                    githubRepoService.unstar({
                        id: id
                    }).$promise.then(function() {
                        _role.stargazers_count--;
                        _role.user_is_stargazer = false;
                        _role.starring = false;
                        currentUserService.update();
                    });
                } else {
                    _role.starring = false;
                }
            }
        }
    }
})(angular);
