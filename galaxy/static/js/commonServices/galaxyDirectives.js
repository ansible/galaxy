/*
 * galaxyDirectives.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    var mod = angular.module('galaxyDirectives', []);

    /*
     * text-collapse used on the role list page
     */
    mod.directive('textCollapse', [_textCollapseDirective]);

    function _textCollapseDirective() {
        return {
            restrict: 'A',
            scope: {
                textCollapseText: '='
            },
            template:
                "<div class=\"collapse-text-area\">{{ displayText }}</div>" +
                "<div ng-show=\"showExpand || showMinus\" class=\"collapse-text-links text-right\">" +
                    "<a href=\"\" ng-show=\"showExpand\" ng-click=\"viewMore()\"><i class=\"fa fa-plus\"></i> More</a>" +
                    "<a href=\"\" ng-show=\"showMinus\" ng-click=\"viewMore()\"><i class=\"fa fa-minus\"></i> Less</a>" +
                "</div>",
            link: _link
        };

        function _link(scope, element, attrs) {
            var textCollapseLimit = parseInt(attrs.textCollapseLimit,10);
            var textCollapseHeight = parseInt(attrs.textCollapseHeight,10);
            if (scope.textCollapseText && scope.textCollapseText.length > textCollapseLimit) {
                _collapse();
            }

            scope.viewMore = function() {
                if (scope.showExpand) {
                    scope.showExpand = false;
                    scope.showMinus = true;
                    scope.displayText = scope.textCollapseText;
                    element.find('.collapse-text-area').css({ height : 'auto' });
                } else {
                    _collapse();
                }
            };

            function _collapse() {
                scope.showExpand = true;
                scope.showMinus = false;
                element.find('.collapse-text-area').css({ height : textCollapseHeight + 'px', 'overflow-y': 'hidden' });
                scope.displayText = scope.textCollapseText.substring(0,textCollapseLimit - 4) + '...';
            }

        }
    }

})(angular);
