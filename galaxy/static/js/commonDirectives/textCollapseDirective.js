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

    var mod = angular.module('textCollapseDirective', []);

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
