


'use strict';

(function(angular) {
    
    var mod = angular.module('listJoinFilter', []);

    mod.filter('listJoin', [_filterFactory]);

    function _filterFactory() {
        return _filter;
    }

    function _filter(input) {
        if (input && input.constructor === Array) {
            var sep = 
            
            result = result.replace(/)
        }
    }
})(angular);