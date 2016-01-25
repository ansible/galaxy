/*
 * dotDotDotDirective.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) { 

    var mod = angular.module('dotDotDotDirective', []);

    mod.directive('dotDotDot', ['$timeout', _directive]);

    function _directive($timeout) {
        return {
            restrict: 'A',
            link: _link
        };

        function _link(scope, element, attr) {
            $timeout(function() {
                $(element).dotdotdot({
                    ellipsis: '...',
                    wrap: 'word',
                    watch: true,
                    fallbackToLetter: true
                });
            }, 500);
        }
    }

})(angular);
