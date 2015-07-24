/*
# (c) 2012-2014, Ansible, Inc. <support@ansible.com>
#
# This file is part of Ansible Galaxy
#
# Ansible Galaxy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible Galaxy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
*/
                
angular.module('Paginate', [])
    
    //Set boundaries of current page range
    //Call from inside scope.refresh()
    .factory('PaginateInit', [ function() {
    return function(params) {
        
        var scope = params.scope; 
        
        scope.getPage = function(n,target) {
            console.log("target is " + target);
            if (target) {
               data = scope.list_data[target];
            } 
            else {
               data = scope.list_data
            }
            data.page = n;
            data.refresh();
            }

        scope.setPageRange = function(target) {
            if (target) {
               data = scope.list_data[target];
            } 
            else {
               data = scope.list_data
            }

            if (data.page % 10 == 0) {
               var first = Math.floor((data.page - 1)/10) * 10 + 1;
            }
            else {
               var first = Math.floor(data.page/10) * 10 + 1;
            }
            first = (first <= 0) ? 1 : first;
            var last = Math.ceil(data.page/10) * 10;
            last = (last > data.num_pages) ? data.num_pages : last;
            for (var i=first; i <= last; i++) {
                //javascript sucks at ranges;
                data.page_range.push(i);
            }
            // These might be out of range, but we'll handle in the view
            data.next_page = last + 1;   
            data.previous_page = first - 1;
            }
        }
        }]);  
