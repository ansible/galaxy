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

    var mod = angular.module('autocompleteDirective', ['ngResource']);

    mod.service('autocompleteService', [_service]);

    mod.directive('autocomplete',['$resource', '$timeout', '$analytics', 'autocompleteService', _directive]);

    function _directive($resource, $timeout, $analytics, autocompleteService) {
        return {
            restrict: 'E',
            templateUrl: '/static/partials/autocomplete.html',
            scope: {
                searchFunction: '=',
                searchSuggestionFunction: '=',
                searchOrderOptions: '=',
                searchTypeOptions: '=',
                searchSuggestions: '=',
                searchPlaceholder: '@',
                searchRoleTypes: '=',
                searchRefreshRoleTypes: '=',
                searchClearRoleTypes: '='
            },
            link: _link
        };

        function _link(scope, element, attr) {
            scope.searchValue = '';
            scope.autocompletePlatforms = [];
            scope.autocompleteTags = [];
            scope.showSearchIcon = true;
            scope.searchType = 'Keyword';
            scope.searchOrder = "";
            scope.searchKeys = [];
            scope.showSearchKeysContainer = true;
            
            scope.searchKeyup = _searchKeyup;
            scope.searchKeydown = _searchKeydown;
            scope.applySuggestion = _suggestionClicked;
            scope.setSearchType = _setSearchType;
            scope.searchAddKey = _searchAddKey;
            scope.addKey = _addKey;
            scope.removeSearchKey = _removeKey;
            scope.changeOrder = _changeOrder;
            scope.getKeywords = _getKeywords;
            scope.setKeywords = _setKeywords;
            scope.toggleSearchKeysContainer = _toggleSearchkeysContainer;
            scope.clearAllSearchKeys = _clearAllSearchKeys;
            scope.suggestionKeyup = _itemKeyup;
            scope.searchFocus = _searchFocus;
            scope.searchBlur = _searchBlur;
            autocompleteService.setScope(scope);

            var originalPlaceholder = scope.searchPlaceholder;
            
            var _lazySuggestions = (scope.searchSuggestionFunction) ? _.debounce(function() {
                scope.searchSuggestions = [];
                scope.searchSuggestionFunction(scope.searchType, scope.searchValue);
            }, 300, true) : null;
            
            var timeoutEventPromise = null;

            $timeout(function() {
                // set focus on the search box after page load
                $('#autocomplete-text-input').focus();
            },300);

            return;


            function _toggleSearchkeysContainer() {
                scope.showSearchKeysContainer = !scope.showSearchKeysContainer;
            }

            function _getKeywords() {
                return scope.searchKeys;
            }

            function _setKeywords(keys) {
                scope.searchKeys = keys;
            }

            function _searchKeyup(e) {
                if (e.keyCode === 13) {
                    //return
                    $timeout.cancel(timeoutEventPromise);
                    $timeout(function() {
                        scope.searchSuggestions = [];
                    }, 300);
                    _searchAddKey();
                    return;
                }
                if (e.keyCode === 40 && scope.searchSuggestions.length) {
                    //down arrow
                    $('#autocomplete-suggestions li a').eq(0).focus();
                    return;
                }
                if (e.keyCode == 27) {
                    $timeout.cancel(timeoutEventPromise);
                    $timeout(function() {
                        scope.searchSuggestions = [];
                    }, 300);
                    return;
                }
                if (scope.searchSuggestionFunction) {
                    if (scope.searchValue.length >= 2 ) {
                        $timeout.cancel(timeoutEventPromise);
                        timeoutEventPromise = $timeout(function() {
                            scope.searchSuggestions = [];
                            scope.searchSuggestionFunction(scope.searchType, scope.searchValue);    
                        }, 300);
                    }
                    else if (scope.searchValue.length === 0) {
                        scope.searchSuggestions = [];
                    }
                }
            }

            function _searchKeydown(e) {
                if (e.keyCode === 9) {
                    // tab
                    $timeout.cancel(timeoutEventPromise);
                    $timeout(function() {
                        scope.searchSuggestions = [];
                    }, 300);
                    if (e.shiftKey) {
                        $('#search-type-button').focus();
                    } else {
                        $('#orderby').focus();
                    }
                    e.preventDefault();
                }
            }

            function _searchFocus(e) {
                // When the search field gets focus, make sure the search type dropdown closes
                $('.autocomplete-search-group .input-group-btn').eq(0).removeClass('open');
                if (scope.searchType == 'Role Type') {
                    scope.searchRefreshRoleTypes(scope.searchValue);
                }
            }

            function _searchBlur(e) {
                if (!e.relatedTarget || e.relatedTarget.offsetParent.id !== 'autocomplete-suggestions') {
                    $timeout(function() {
                        scope.searchSuggestions = [];
                    }, 300);
                }
            }

            function _itemKeyup(e) {
                // Use up/down arrow to traverse suggestions list
                if (e.keyCode === 40) {
                    //down arrow
                    $(e.currentTarget).next().eq(0).find('a').eq(0).focus();
                    e.preventDefault();
                    return;
                }
                if (e.keyCode === 38) {
                    //up arrow
                    if (parseInt($(e.currentTarget).attr('data-index'),10) === 0) {
                        $('#autocomplete-text-input').focus();
                    }
                    $(e.currentTarget).prev().eq(0).find('a').eq(0).focus();
                    e.preventDefault();
                }
            }

            function _setSearchType(type) {
                scope.searchType = type;
                if (type == 'Role Type') {
                    scope.searchPlaceholder = 'Choose from option list'
                    scope.searchRefreshRoleTypes(scope.searchValue);
                    scope.showSearchIcon = false;
                } else {
                    scope.showSearchIcon = true;
                    scope.searchPlaceholder = originalPlaceholder;
                }
                $('#autocomplete-text-input').focus();
            }

            function _searchAddKey() {
                if (scope.searchValue) {
                    _addKey({ value: scope.searchValue, type: scope.searchType });
                    scope.searchValue = null;
                }
            }

            function _addKey(_key) {
                var found = false;
                angular.forEach(scope.searchKeys, function(key) {
                    if (key.value === _key.value && key.type === _key.type) {
                        found = true;
                    }
                });
                if (!found) {
                    var event_track = {
                        category: _key.type + ': ' + _key.value
                    };
                    $analytics.eventTrack('search_key', event_track);
                    scope.searchKeys.push(_key);
                    scope.searchFunction(scope.searchKeys, scope.searchOrder);
                }
            }

            function _removeKey(_key) {
                scope.searchKeys.every(function(key, idx) {
                    if (key.value === _key.value && key.type === _key.type) {
                        scope.searchKeys.splice(idx, 1);
                        return false;
                    }
                    return true;
                });
                scope.searchFunction(scope.searchKeys, scope.searchOrder);
            }

            function _clearAllSearchKeys() {
                scope.searchKeys = [];
                scope.searchFunction(scope.searchKeys, scope.searchOrder);
            }

            function _changeOrder() {
                scope.searchFunction(scope.searchKeys, scope.searchOrder);
            }

            function _suggestionClicked(suggestion) {
                scope.searchSuggestions = [];
                scope.searchValue = suggestion.name;
                _searchAddKey();
            }
        }
    }

    // 
    // Use autocompleteService to access and control the search widget from a controller
    //
    function _service() {
        var scope;

        return {
            setScope: _setScope,
            getKeywords: _getKeywords,
            setKeywords: _setKeywords,
            addKey: _addKey,
            removeKey: _removeKey,
            setOrderBy: _setOrderBy
        };

        function _setScope(_scope) {
            scope = _scope;
        }
        
        function _addKey(_key) {
            scope.addKey(_key);
        }

        function _removeKey(_key) {
            scope.removeSearchKey(_key);
        }

        function _getKeywords() {
            return scope.getKeywords();
        }

        function _setKeywords(keywords) {
            scope.setKeywords(keywords);
        }

        function _setOrderBy(order) {
            scope.searchOrder = order;
        }
    }

 })(angular);
