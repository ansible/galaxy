/*
 * searchService.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */

'use strict';

(function(angular) {

    angular.module('searchService', ['galaxyUtilities'])
        .factory('SearchInit', ['Empty', _factory]);

    // Init search related functions into the scope object
    var Empty;

    function _factory(_Empty) {
        Empty = _Empty;
        return _searchInit;
    }

    function _searchInit(params) {

        var scope = params.scope;
        scope.searchPlaceHolder = params.placeHolder;
        scope.sort_options = params.sortOptions;   //Expects [ { label:'', value: '' },...]
        scope.showSearchIcon = params.showSearchIcon;

        if (params.platforms) {
            scope.platforms = params.platforms;
            scope.showPlatforms = true;
        }

        scope.sort = { obj: {} };   //For reasons unknown the model has to be an object. Makes no sense, but it works.
        scope.sort.platform = null;

        scope.setSortOrder = function(val) {
            //pass in a string that matches one of the sort values, and
            //we'll set to the drop-down to the matching array value.
            var found = false;
            for (var i=0; i < scope.sort_options.length; i++) {
                if (scope.sort_options[i].value === val) {
                    scope.sort.obj = scope.sort_options[i];
                    found = true;
                    break;
                }
            }
            return found;   //let the caller know if we found and set the value
        };

        scope.setSortOrder(params.sortOrder);

        scope.getSortOrder = function() {
            // Return the string value representing the drop-down's current value.
            // If the value is null, force select to the first option in the list. Null
            // is not allowed.
            if (scope.sort.obj && scope.sort.obj.value) {
                return scope.sort.obj.value;
            }
            scope.sort.obj = scope.sort_options[0];
            return scope.sort.obj.value;
        };

        //Set the search icon. When user clicks toggle.
        scope.toggleSearchIcon = function() {
            if (scope.showSearchIcon && !Empty(scope.list_data.list_filter)) {
               // user typed value and clicked search icon
               scope.showSearchIcon = false;
            }
            else if (!scope.showSearchIcon) {
               // user clicked clear
               scope.list_data.list_filter = null;
               scope.showSearchIcon = true;
            }
            scope.list_data.refresh();
        };

        // User changed search value and clicked icon or pressed enter
        scope.applyFilter = function(e) {
            if (e.keyCode == 13) {
                // User clicked enter key, start the search
                scope.list_data.refresh();

                // When a value was entered, hide search icon and show cancel
                if (!Empty(scope.list_data.list_filter)) {
                   scope.showSearchIcon = false;
                }
                else {
                   scope.showSearchIcon = true;
                }
            }
        };
    }
})(angular);
