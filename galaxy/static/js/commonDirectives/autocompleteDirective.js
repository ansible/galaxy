/*
 * autoCompletDirective.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

 'use strict';

 (function(angular) {

    var mod = angular.module('autocompleteDirective', ['ngResource']);

    mod.directive('autocomplete',['$resource', '$timeout', _directive]);

    function _directive($resource, $timeout) {
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
            scope.searchKeyup = _keyup;
            scope.searchValue = null;
            scope.autocompletePlatforms = [];
            scope.autocompleteTags = [];
            scope.focus = _focus;
            scope.blur = _blur;
            scope.applySuggestion = _suggestionClicked;
            scope.showSearchIcon = true;
            scope.searchType = 'Keyword';
            scope.setSearchType = _setSearchType;
            scope.searchKeys = [];
            scope.searchAddKey = _addKey;
            scope.removeSearchKey = _removeKey;
            scope.searchOrder = "";
            scope.changeOrder = _changeOrder;

            var _lazySuggestions = (scope.searchSuggestionFunction) ? _.debounce(function() { 
                scope.searchSuggestionFunction(scope.searchType, scope.searchValue);
            }, 300, true) : null;
                
            function _keyup(e) {
                scope.searchSuggestions = [];
                if (e.keyCode == 13) {
                    _addKey();
                    return;
                }
                if (scope.searchSuggestionFunction) {
                    _lazySuggestions();
                }
            }

            function _focus() {
            //    scope.showResults = true;
            }

            function _blur() {
            //    $timeout(function() {
            //        scope.showResults = false;
            //    },300);
            }

            function _suggestionClicked(suggestion) {
            //    if (scope.searchSuggestionFunction) {
            //        scope.searchSuggestionFunction(suggestion)
            //    }
            }

            function _setSearchType(type) {
                scope.searchType = type;
            }

            function _addKey() {
                if (scope.searchValue) {
                    var found = false;
                    angular.forEach(scope.searchKeys, function(key) {
                        if (key.value === scope.searchValue && key.type === scope.searchType) {
                            found = true;
                        }
                    });
                    if (!found) {
                        scope.searchKeys.push({
                            value: scope.searchValue,
                            type: scope.searchType,
                        });
                    }
                    scope.searchValue = null;
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

            function _changeOrder() {
                scope.searchFunction(scope.searchKeys, scope.searchOrder);
            }

            function _suggestionClicked(suggestion) {
                scope.searchSuggestions = [];
                scope.searchValue = suggestion.name;
                _addKey();
            }
        }
    }

 })(angular);