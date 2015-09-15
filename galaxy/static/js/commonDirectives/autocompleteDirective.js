/*
 * autoCompletDirective.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

 'use strict';

 (function(angular) {

    var mod = angular.module('autocompleteDirective', ['ngResource']);

    mod.service('autocompleteService', [_service]);

    mod.directive('autocomplete',['$resource', '$timeout', 'autocompleteService', _directive]);

    function _directive($resource, $timeout, autocompleteService) {
        return {
            restrict: 'E',
            templateUrl: '/static/partials/autocomplete.html',
            scope: {
                searchFunction: '=',
                searchSuggestionFunction: '=',
                searchOrderOptions: '=',
                searchTypeOptions: '=',
                searchSuggestions: '=',
                searchPlaceholder: '@'
            },
            link: _link
        };

        function _link(scope, element, attr) {
            scope.searchValue = null;
            scope.autocompletePlatforms = [];
            scope.autocompleteTags = [];
            scope.showSearchIcon = true;
            scope.searchType = 'Keyword';
            scope.searchOrder = "";
            scope.searchKeys = [];
            scope.showSearchKeysContainer = true;
            
            scope.searchKeyup = _keyup;
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

            autocompleteService.setScope(scope);
            
            var _lazySuggestions = (scope.searchSuggestionFunction) ? _.debounce(function() {
                scope.searchSuggestions = [];
                scope.searchSuggestionFunction(scope.searchType, scope.searchValue);
            }, 300, true) : null;
            
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

            function _keyup(e) {
                if (e.keyCode == 13) {
                    scope.searchSuggestions = [];
                    _searchAddKey();
                    return;
                }
                if (scope.searchSuggestionFunction) {
                    _lazySuggestions();
                }
            }

            function _setSearchType(type) {
                scope.searchType = type;
            }

            function _searchAddKey() {
                _addKey({ value: scope.searchValue, type: scope.searchType });
                scope.searchValue = null;
            }

            function _addKey(_key) {
                var found = false;
                angular.forEach(scope.searchKeys, function(key) {
                    if (key.value === _key.value && key.type === _key.type) {
                        found = true;
                    }
                });
                if (!found) {
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