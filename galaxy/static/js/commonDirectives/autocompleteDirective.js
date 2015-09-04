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
                searchOnkeyup: '=',
                searchSuggestions: '=',
                searchFunction: '=',
                searchSuggestionFunction: '='
            },
            link: _link
        };

        function _link(scope, element, attr) {
            scope.searchPlaceholder = attr.searchPlaceholder;
            scope.searchKeyup = _keyup;
            scope.searchValue = null;
            scope.autocompletePlatforms = [];
            scope.autocompleteTags = [];
            scope.focus = _focus;
            scope.blur = _blur;
            scope.suggestionClicked = _suggestionClicked;

            if (scope.searchFunction)
                var lazySearch = _.debounce(function() { scope.searchFunction(scope.searchValue); }, 300);

            if (scope.searchOnkeyup)
                var lazyKeyup = _.throttle(function() { scope.searchOnkeyup(scope.searchValue); }, 100);

            function _keyup(e) {
                scope.showResults = true;
                if (e.keyCode == 13 || e.keyCode == 9 || e.keyCode == 27) {
                    scope.showResults = false;
                    return;
                }
                if (scope.searchValue.length >= 3 && scope.searchOnkeyup)
                    scope.searchOnkeyup(scope.searchValue);

                if ((scope.searchValue.length === 0 || scope.searchValue.length >= 3) && scope.searchFunction)
                    scope.searchFunction(scope.searchValue);
            }

            function _focus() {
                scope.showResults = true;
            }

            function _blur() {
                $timeout(function() {
                    scope.showResults = false;
                },300);
            }

            function _suggestionClicked(suggestion) {
                if (scope.searchSuggestionFunction) {
                    scope.searchSuggestionFunction(suggestion)
                }
            }
        }
    }

 })(angular);