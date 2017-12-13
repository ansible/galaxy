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
    
    var mod = angular.module('roleListController', ['ngResource']);

    mod.controller('RoleListCtrl', [
        '$scope',
        '$routeParams',
        '$location',
        '$timeout',
        '$resource',
        '$window',
        '$log',
        '$analytics',
        'roleSearchService',
        'queryStorageFactory',
        'Empty',
        'SearchInit',
        'PaginateInit',
        'platformService',
        'autocompleteService',
        'githubRepoService',
        'currentUserService',
        'githubClickService',
        _RoleListCtrl
    ]);

    function _RoleListCtrl(
        $scope,
        $routeParams,
        $location,
        $timeout,
        $resource,
        $window,
        $log,
        $analytics,
        roleSearchService,
        queryStorageFactory,
        Empty,
        SearchInit,
        PaginateInit,
        platformService,
        autocompleteService,
        githubRepoService,
        currentUserService,
        githubClickService) {

        $('#bs-example-navbar-collapse-1').removeClass('in');  //force collapse of mobile navbar
        $('#galaxy-copyright').hide();
        $('#galaxy-footer-blue-line').hide();

        $scope.page_title = 'Search';
        $scope.version = GLOBAL_VERSION;
        
        $scope.orderOptions = [
            { value:"name,username", title:"Name" },
            { value:"username,name", title:"Author" },
            { value:"-created,name", title:"Created" },
            { value:"-stargazers_count,name", title: "Stargazers" },
            { value:"-watchers_count,name", title: "Watchers"},
            { value:"-download_count,name", title: "Downloads"}
        ];

        $scope.searchTypeOptions = [
            'Author',
            'Keyword',
            'Platform',
            'Cloud Platform',
            'Tag',
            'Role Type'
        ];


        $scope.list_data = {
            'num_pages'          : 1,
            'page'               : 1,
            'page_size'          : '10',
            'page_range'         : [],
            'tags'               : '',
            'platforms'          : '',
            'cloud_platforms'    : '',
            'users'              : '',
            'role_type'          : '',
            'autocomplete'       : '',
            'order'              : $scope.orderOptions[5].value,
            'refresh'            : _refresh
        };

        $scope.searchRoleTypes = [
            { value: "CON", title: "Container Enabled" },
            { value: "APP", title: "Container App" }
        ];

        $scope.page_range = [1];
        $scope.categories = [];
        $scope.roles = [];
        $scope.num_roles = 0;
        $scope.status = '';

        $scope.loading = 1;
        $scope.viewing_roles = 1;
        $scope.display_user_info = 1;
        $scope.topTags = [];
        $scope.topCloudTags = [];
        $scope.topPlatformTags = [];
        
        // autocomplete functions
        $scope.search = _search;
        $scope.searchSuggestion = _searchSuggestion;
        $scope.searchSuggesions = [];

        $scope.activateTag = _activateTag;
        $scope.activatePlatform = _activatePlatform;
        $scope.activateCloudPlatform = _activateCloudPlatform;
        $scope.changeOrderby = _changeOrderby;
        
        $scope.$on('endlessScroll:next', _loadNextPage);

        $scope.subscribe = githubClickService.subscribe;
        $scope.unsubscribe = githubClickService.unsubscribe;
        $scope.star = githubClickService.star;
        $scope.unstar = githubClickService.unstar;
        $scope.is_authenticated = currentUserService.authenticated && currentUserService.connected_to_github;

        $scope.refreshRoleTypes = _refreshRoleTypes;
        $scope.clearRoleTypes = _clearRoleTypes;

        PaginateInit({ scope: $scope });

        var suggestions = $resource('/api/v1/search/:object/', { 'object': '@object', 'page': 1, 'page_size': 10 }, {
            'tags': { method: 'GET', params:{ object: 'tags' }, isArray: false },
            'platforms': { method: 'GET', params:{ object: 'platforms' }, isArray: false },
            'cloud_platforms': { method: 'GET', params:{ object: 'cloud_platforms' }, isArray: false },
            'users': { method: 'GET', params:{ object: 'users' }, isArray: false }
        });

        // Load the initial query parameters into $scope.list_data
        var restored_query = queryStorageFactory.restore_state(_getQueryParams($scope.list_data));
        $scope.list_data = angular.extend({}, $scope.list_data, _getQueryParams(restored_query));

        _getTopTags();
        _getTopCloudTags();
        _getTopPlatformTags();
        _refresh();

        $timeout(function() {
            // Match the autocomplete widget to query params
            _setSearchTerms($scope.list_data);
            _setOrderBy();
            _updateTopTags();
        }, 500);

        $scope.$on('$destroy', function() {
            $('#galaxy-copyright').show();
            $('#galaxy-footer-blue-line').show();
        });
        
        return;

        function _getTopTags() {
            suggestions.tags({ page: 1, page_size: 15, order: '-roles' }).$promise.then(function(data) {
                $scope.topTags = data.results;
            });
        }

        function _getTopCloudTags() {
            suggestions.cloud_platforms({ page: 1, page_size: 15}).$promise.then(function(data) {
                $scope.topCloudTags = data.results;
            });
        }

        function _getTopPlatformTags() {
            suggestions.platforms({ page: 1, page_size: 15, order: '-roles' }).$promise.then(function(data) {
                $scope.topPlatformTags = data.results;
            });
        }


        function _changeOrderby() {
            _refresh();
        }

        function _refresh() {
            $scope.loading = 1;
            $scope.roles = [];

            var page_size = parseInt($scope.list_data.page_size,10);
            if (page_size <= 0)
                $scope.list_data.page_size = 10;
            if (page_size > 100)
                $scope.list_data.page_size = 100;

            var page = parseInt($scope.list_data.page,10);
            if (page <= 0)
                $scope.list_data.page = 1;

            var params = {
                page: $scope.list_data.page,
                page_size: $scope.list_data.page_size
            };

            var event_track = {
                category: ''
            };

            if ($scope.list_data.autocomplete) {
                params.autocomplete = $scope.list_data.autocomplete;
                event_track.category += '/Keywords:' + params.autocomplete; 
            }

            if ($scope.list_data.tags) {
                params.tags_autocomplete = $scope.list_data.tags;
                event_track.category += '/Tags:' + params.tags_autocomplete;
            }

            if ($scope.list_data.platforms) {
                params.platforms_autocomplete = $scope.list_data.platforms;
                event_track.category += '/Platforms:' + params.platforms_autocomplete;
            }

            if ($scope.list_data.cloud_platforms) {
                params.cloud_platforms_autocomplete = $scope.list_data.cloud_platforms;
                event_track.category += '/CloudPlatforms:' + params.cloud_platforms_autocomplete;
            }

            if ($scope.list_data.users) {
                params.username_autocomplete = $scope.list_data.users;
                event_track.category += '/Authors:' + params.username_autocomplete;
            }

            if ($scope.list_data.role_type) {
                params.role_type = $scope.list_data.role_type;
                event_track.category += '/RoleType:' + params.role_type;
            }

            if ($scope.list_data.order) {
                params.order = $scope.list_data.order;
                event_track.category += '/Order:' + params.order;
            }
            
            if (Object.keys(params).length == 2) {
                // no parameters
                params.order = 'role_id';
                event_track.category += '/Order: role_id'
            }

            event_track.category = event_track.category.replace(/^\//,'');
            $analytics.eventTrack('search', event_track);
                
            // Update the query string
            queryStorageFactory.save_state(_queryParams($scope.list_data));

            const ROLE_TYPES = {
                ANS: 'Ansible',
                CON: 'Container Enabled',
                APP: 'Container App',
                DEM: 'Demo'
            };

            return roleSearchService.get(params)
                .$promise.then(function(data) {
                    angular.forEach(data.results, function(row) {
                        row.display_type = row.role_type;
                        row.display_type_title = ROLE_TYPES[row.role_type];
                    });
                    $scope.roles = data.results;
                    $scope.status = "";
                    $scope.loading = 0;

                    $scope.list_data.page = parseInt(data['cur_page']);
                    $scope.list_data.num_pages = parseInt(data['num_pages']);
                    $scope.list_data.count = parseInt(data['count']);
                    
                    $scope.list_data.page_range = [];
                    $scope.setPageRange();
                    _resizeSearchControls();
                });
        }

        function _loadNextPage() {
            if (!$scope.loading && $scope.list_data.page < $scope.list_data.num_pages) {
                $scope.list_data.page++;
                _refresh();
            }
        }

        function _doActivateTag(name, tagType, listDataAttr) {
            autocompleteService.addKey({ type: tagType, value: name });
            $scope.list_data[listDataAttr] = autocompleteService.getKeywords().filter(function(key) {
                return (key.type === tagType);
            }).map(function(tag) { return tag.value; }).join(' ');
            $log.debug($scope.list_data);
            _refresh();
        }

        function _activateTag(name) {
            _doActivateTag(name, 'Tag', 'tags');
        }

        function _activatePlatform(name) {
            _doActivateTag(name, 'Platform', 'platforms');
        }

        function _activateCloudPlatform(name) {
            _doActivateTag(name, 'Cloud Platform', 'cloud_platforms');
        }

        function _search(_keywords, _orderby) {
            $scope.list_data.page = 1;
            $scope.roles = [];
            var tags = [], platforms = [], cloud_platforms = [],
                keywords = [], users = [], role_type = [], params = {};
            angular.forEach(_keywords, function(keyword) {
                if (keyword.type === 'Tag') {
                    tags.push(keyword.value);
                } else if (keyword.type === 'Platform') {
                    platforms.push(keyword.value);
                } else if (keyword.type === 'Cloud Platform') {
                    cloud_platforms.push(keyword.value);
                } else if (keyword.type === 'Author') {
                    users.push(keyword.value);
                } else if (keyword.type === 'Role Type') {
                    angular.forEach($scope.searchRoleTypes, function(rt) {
                        if (rt.title == keyword.value) {
                            role_type.push(rt.value);
                        }
                    });
                } else {
                    keywords.push(keyword.value);
                }
            });
            $scope.list_data.platforms = '';
            $scope.list_data.cloud_platforms = '';
            $scope.list_data.autocomplete = '';
            $scope.list_data.order = '';
            $scope.list_data.tags = '';
            $scope.list_data.users = '';
            $scope.list_data.role_type = '';
            if (tags.length) {
                $scope.list_data.tags = tags.join(' ');
            }
            if (platforms.length) {
                $scope.list_data.platforms = platforms.join(' ');
            }
            if (cloud_platforms.length) {
                $scope.list_data.cloud_platforms = cloud_platforms.join(' ');
            }
            if (keywords.length) {
                $scope.list_data.autocomplete = keywords.join(' ');
            }
            if (users.length) {
                $scope.list_data.users = users.join(' ');
            }
            if (role_type.length) {
                $scope.list_data.role_type = role_type.join(',');
            }
            if (_orderby) {
                $scope.list_data.order = _orderby.value;
            }
            _updateTopTags(tags);
            _refresh();
        }

        function _updateTopTags() {
            // reset the active state of our topTags
            var _tags = autocompleteService.getKeywords()
                .filter(function(_key) { return (_key.type === 'Tag'); })
                .map(function(_key) { return _key.value });
            $scope.topTags.forEach(function(tag) { tag.active = false; });
            $scope.topTags.forEach(function(tag) {
                var found = _.find(_tags, function(_tag) { return (_tag === tag.tag); });
                if (found) {
                    tag.active = true;
                }
            });
        }

        function _searchSuggestion(type, value) {
            $scope.searchSuggestions = [];
            if (type ===  'Tag' && value) {
                suggestions.tags({ autocomplete: value}).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Tag',
                            name: result.tag
                        });
                    });
                });
            } else if (type === 'Platform' && value) {
                suggestions.platforms({ autocomplete: value }).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Platform',
                            name: result.name
                        });
                    });
                });
            } else if (type === 'Cloud Platform' && value) {
                suggestions.cloud_platforms({ autocomplete: value }).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Cloud Platform',
                            name: result.name
                        });
                    });
                });
            } else if (type === 'Author' && value) {
                suggestions.users({ autocomplete: value }).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Author',
                            name: result.username
                        });
                    });
                });
            } else if (type === 'Role Type' && value) {
                angular.forEach($scope.searchRoleTypes, function(role_type) {
                    if (role_type.title.toLowerCase().includes(value.toLowerCase())) {
                        $scope.searchSuggestions.push({
                            type: 'Role Type',
                            name: role_type.title
                        });
                    }
                });
            }
        }

        function _queryParams() {
            var result = {};
            if ($scope.list_data.page) {
                result.page = $scope.list_data.page;
            }
            if ($scope.list_data.page_size) {
                result.page_size = $scope.list_data.page_size;
            }
            if ($scope.list_data.tags) {
                result.tags = $scope.list_data.tags;
            }
            if ($scope.list_data.platforms) {
                result.platforms = $scope.list_data.platforms;
            }
            if ($scope.list_data.cloud_platforms) {
                result.cloud_platforms = $scope.list_data.cloud_platforms;
            }
            if ($scope.list_data.users) {
                result.users = $scope.list_data.users;
            }
            if ($scope.list_data.autocomplete) {
                result.autocomplete = $scope.list_data.autocomplete;
            }
            if ($scope.list_data.order) {
                result.order = $scope.list_data.order;
            }
            if ($scope.list_data.role_type) {
                result.role_type = $scope.list_data.role_type;
            }
            return result;
        }

        function _getQueryParams(data)  {
            var result = {};
            result.page = data.page || 1;
            result.page_size = data.page_size || 10;
            result.tags = data.tags || '';
            result.platforms = data.platforms || '';
            result.cloud_platforms = data.cloud_platforms || '';
            result.users = data.users || '';
            result.autocomplete = data.autocomplete || '';
            result.order = data.order || '';
            result.role_type = data.role_type || '';
            return result;
        }

        function _setSearchTerms(data) {
            var keys = [];
            if (data.platforms) {
                _getKeys('Platform', data.platforms, keys);
            }
            if (data.cloud_platforms) {
                _getKeys('Cloud Platform', data.cloud_platforms, keys);
            }
            if (data.tags) {
                _getKeys('Tag', data.tags, keys);
            }
            if (data.autocomplete) {
                _getKeys('Keyword', data.autocomplete, keys);
            }
            if (data.users) {
                _getKeys('Author', data.users, keys);
            }
            if (data.role_type) {
                _getKeys('Role Type', data.role_type, keys);
            }
            var uniqKeys = _.uniq(keys, false, function(val) { return val.type + ':' + val.value; });
            autocompleteService.setKeywords(uniqKeys);
        }

        function _setOrderBy() {
            $scope.orderOptions.every(function(option) {
                if (option.value === $scope.list_data.order) {
                    autocompleteService.setOrderBy(option);
                    return false;
                }
                return true;
            });
        }

        function _getKeys(type, data, results) {
            data.split(' ').forEach(function(key) {
                if (type == 'Role Type') {
                    angular.forEach($scope.searchRoleTypes, function(rt) {
                        if (rt.value == key) {
                            results.push({
                                type: type,
                                value: rt.title
                            });
                        }
                    });
                } else {
                    results.push({
                        type: type,
                        value: key
                    });
                }
            });
        }

        function _refreshRoleTypes(value) {
            $scope.searchSuggestions = [];
            angular.forEach($scope.searchRoleTypes, function(role_type) {
                if (value) {
                    if (role_type.title.toLowerCase().includes(value.toLowerCase())) {
                        $scope.searchSuggestions.push({
                            type: 'Role Type',
                            name: role_type.title
                        });
                    }
                } else {
                    $scope.searchSuggestions.push({
                        type: 'Role Type',
                        name: role_type.title
                    });
                }
            });
        }

        function _clearRoleTypes() {
            $scope.searchSuggestions = [];
        }

        function _resizeSearchControls() {
            var containerHeight = $('#search-control-container').outerHeight();
            $log.debug('setting #role-list-results:height to ' + (containerHeight + 1));
            $('#role-list-results').css({ 'padding-top': (containerHeight + 1) + 'px'});
        }

        function _resizeTagsContainer() {
            // adjust height of tags container
            var containerHeight = $($window).height() - 260; //max height
            var tagsHeight = ($scope.topTags.length * 28) + 75;
            $log.debug('containerHeight: ' + containerHeight);
            $('#role-tags-container').css({ 'height': Math.min(containerHeight, tagsHeight) + 'px' });
            $('#role-tags-container .body-wrapper').css({ 'height': (Math.min(containerHeight, tagsHeight) - 20) + 'px '});
        }
    }
})(angular);
