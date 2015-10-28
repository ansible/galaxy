/*
 * roleListController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
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
        'roleFactory',
        'roleSearchService',
        'queryStorageFactory',
        'my_info',
        'Empty',
        'SearchInit',
        'PaginateInit',
        'platformService',
        'autocompleteService',
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
        roleFactory,
        roleSearchService,
        queryStorageFactory,
        my_info,
        Empty,
        SearchInit,
        PaginateInit,
        platformService,
        autocompleteService) {

        
        $scope.page_title = 'Browse Roles';
        $scope.my_info = my_info;

        $scope.list_data = {
            'num_pages'          : 1,
            'page'               : 1,
            'page_size'          : 10,
            'page_range'         : [],
            'tags'               : '',
            'platforms'          : '',
            'users'              : '',
            'autocomplete'       : '',
            'order'              : '',
            'refresh'            : _refresh
        };

        $scope.orderOptions = [
            { value:"-created", title: "Created" },
            { value:"name,username", title:"Name" },
            { value:"username,name", title:"Author" },
            { value:"-average_score,sort_name,username", title:"Score" }
        ];

        $scope.searchTypeOptions = [
            'Author',
            'Keyword',
            'Platform',
            'Tag'
        ];

        $scope.page_range = [1];
        $scope.categories = [];
        $scope.roles = [];
        $scope.num_roles = 0;
        $scope.status = '';

        $scope.loading = 1;
        $scope.viewing_roles = 1;
        $scope.display_user_info = 1;
        $scope.searchSuggestions = [];
        $scope.topTags = [];
        
        // autocomplete functions
        $scope.search = _search;
        $scope.searchSuggestion = _searchSuggestion;
        $scope.searchSuggesions = [];

        $scope.activateTag = _activateTag;
        $scope.changeOrderby = _changeOrderby;
        
        $scope.$on('endlessScroll:next', _loadNextPage);

        PaginateInit({ scope: $scope });

        var suggestions = $resource('/api/v1/search/:object/', { 'object': '@object', 'pagge': 1, 'page_size': 10 }, {
            'tags': { method: 'GET', params:{ object: 'tags' }, isArray: false },
            'platforms': { method: 'GET', params:{ object: 'platforms' }, isArray: false },
            'users': { method: 'GET', params:{ object: 'users' }, isArray: false }
        });

        // Load the initial query parameters into $scope.list_data
        var restored_query = queryStorageFactory.restore_state(_getQueryParams($scope.list_data));
        $scope.list_data = angular.extend({}, $scope.list_data, _getQueryParams(restored_query));

        var lazy_resize = _.debounce(function() { 
            _windowResize();
        }, 500);

        $($window).resize(lazy_resize);
       
        _getTopTags();
        _refresh().then(lazy_resize);
        
        $timeout(function() {
            // Match the autocomplete widget to query params
            _windowResize();
            _setSearchTerms($scope.list_data);
            _setOrderBy();
            _updateTopTags();
        }, 500);

        $scope.$on('$destroy', function() {
            $('body').css({ 'overflow-y': 'auto', 'height': '100%' });
        });
        
        return;

        function _getTopTags() {
            suggestions.tags({ page: 1, page_size: 9999, order: '-roles' }).$promise.then(function(data) {
                $scope.topTags = data.results;
            });
        }

        function _changeOrderby() {
            _refresh();
        }

        function _refresh() {
            $scope.loading = 1;
            $scope.roles = [];
            
            var params = {
                page: $scope.list_data.page,
                page_size: $scope.list_data.page_size,
            };
            
            if ($scope.list_data.order) {
                params.order = $scope.list_data.order;
            }

            if ($scope.list_data.tags) {
                params.tags_autocomplete = $scope.list_data.tags;
            }

            if ($scope.list_data.platforms) {
                params.platforms_autocomplete = $scope.list_data.platforms;
            }

            if ($scope.list_data.users) {
                params.username_autocomplete = $scope.list_data.users;
            }

            if ($scope.list_data.autocomplete) {
                params.autocomplete = $scope.list_data.autocomplete;
            }

            // Update the query string
            queryStorageFactory.save_state(_queryParams($scope.list_data));

            return roleSearchService.get(params)
                .$promise.then(function(data) {
                    $scope.roles = data.results;
                    $scope.status = "";
                    $scope.loading = 0;

                    $scope.list_data.page = parseInt(data['cur_page']);
                    $scope.list_data.num_pages = parseInt(data['num_pages']);
                    $scope.list_data.count = parseInt(data['count']);
                    
                    $scope.list_data.page_range = [];
                    $scope.setPageRange();
                    _resizeSearchControls();
                    $timeout(_windowResize, 500);
                });
        }

        function _loadNextPage() {
            if (!$scope.loading && $scope.list_data.page < $scope.list_data.num_pages) {
                $scope.list_data.page++;
                _refresh();
            }
        }

        function _activateTag(tag) {
            tag.active = !tag.active;
            if (tag.active) {
                $log.debug('Add tag: ' + tag.tag);
                autocompleteService.addKey({ type: 'Tag', value: tag.tag });
            } else {
                $log.debug('Remove tag: ' + tag.tag);
                autocompleteService.removeKey({ type: 'Tag', value: tag.tag });
            }
            $scope.list_data.tags = autocompleteService.getKeywords().filter(function(key) {
                return (key.type === 'Tag');
            }).map(function(tag) { return tag.value; }).join(' ');
            $log.debug($scope.list_data);
            _refresh();
        }

        function _search(_keywords, _orderby) {
            $scope.list_data.page = 1;
            $scope.roles = [];
            var tags = [], platforms = [], keywords = [], users = [], params = {};
            angular.forEach(_keywords, function(keyword) {
                if (keyword.type === 'Tag') {
                    tags.push(keyword.value);
                } else if (keyword.type === 'Platform') {
                    platforms.push(keyword.value);
                } else if (keyword.type === 'Author') {
                    users.push(keyword.value);
                } else {
                    keywords.push(keyword.value);
                }
            });
            $scope.list_data.platforms = '';
            $scope.list_data.autocomplete = '';
            $scope.list_data.order = '';
            $scope.list_data.tags = '';
            $scope.list_data.users = '';
            if (tags.length) {
                $scope.list_data.tags = tags.join(' ');
            }
            if (platforms.length) {
                $scope.list_data.platforms = platforms.join(' ');
            }
            if (keywords.length) {
                $scope.list_data.autocomplete = keywords.join(' ');
            }
            if (users.length) {
                $scope.list_data.users = users.join(' ');
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
            } else if (type === 'Author' && value) {
                suggestions.users({ autocomplete: value }).$promise.then(function(data) {
                    angular.forEach(data.results, function(result) {
                        $scope.searchSuggestions.push({
                            type: 'Author',
                            name: result.username
                        });
                    });
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
            if ($scope.list_data.users) {
                result.users = $scope.list_data.users;
            }
            if ($scope.list_data.autocomplete) {
                result.autocomplete = $scope.list_data.autocomplete;
            }
            if ($scope.list_data.order) {
                result.order = $scope.list_data.order;
            }
            return result;
        }

        function _getQueryParams(data)  {
            var result = {};
            result.page = data.page || 1;
            result.page_size = data.page_size || 10;
            result.tags = data.tags || '';
            result.platforms = data.platforms || '';
            result.users = data.users || '';
            result.autocomplete = data.autocomplete || '';
            result.order = data.order || '';
            return result;
        }

        function _setSearchTerms(data) {
            var keys = []
            if (data.platforms) {
                _getKeys('Platform', data.platforms, keys);
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
                results.push({
                    type: type,
                    value: key
                });
            });
        }

        function _windowResize() {
            var windowHeight = $($window).height();
            var searchHeight = $('#role-list-search').outerHeight() + 20;
            var footerHeight = 0;
            /*if ($($window).width() > 768) {
                footerHeight = $('#galaxy-footer').outerHeight() +
                    $('galaxy-footer-blue-line').outerHeight() + $('#galaxy-copyright').outerHeight() + 15;
            }*/
            var newHeight = windowHeight - 140 - searchHeight - footerHeight;
            $log.debug('searchHeight: ' + searchHeight + ' footerHeight: ' + footerHeight);
            $('#results-container').height(newHeight);
            $('body').css({ 'overflow-y': 'hidden', 'height': 'auto' });

            var containerWidth = $('#results-column').width();
            var resultWidth = $('#results-container .result').eq(0).outerWidth() + 10;
            var cnt = Math.floor(containerWidth / resultWidth);
            var newWidth = cnt * resultWidth;
            var padding = Math.floor((containerWidth - newWidth) / 2)
            $log.debug('containerWidth: ' + containerWidth + ' resultWidth: ' + resultWidth + ' cnt: ' + cnt + ' newWidth: ' + newWidth);
            if (cnt && newWidth < containerWidth) {
                $('#results-container').css({ 'padding-left': padding, 'padding-right': padding });
            } else {
                $('#results-container').css({ 'padding-left': 0, 'padding-right': 0 });
            }
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
            $('#role-tags-container .body').css({ 'height': (Math.min(containerHeight, tagsHeight) - 80) + 'px '});
        }
    }
})(angular);