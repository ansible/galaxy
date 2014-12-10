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

'use strict';

/* Controllers */

var listControllers = angular.module('listControllers', ['Utilities', 'Search']);

listControllers.controller('RoleListCtrl', ['$scope','$routeParams','$location','$timeout','roleFactory','categoryFactory',
'storageFactory','my_info', 'Empty', 'SearchInit', 'PaginateInit',
function($scope, $routeParams, $location, $timeout, roleFactory, categoryFactory, storageFactory, my_info, Empty, SearchInit, PaginateInit) {
    
    //$scope.orderby={ sort_order: 'owner__username,name' };
    $scope.page_title = 'Browse Roles';
    $scope.my_info = my_info;
     
    $scope.list_data = {
        'list_filter'        : '',
        'num_pages'          : 1,
        'page'               : 1,
        'results_per_page'   : 10,
        'reverse'            : false,
        'selected_categories': [],
        'sort_order'         : 'owner__username,name',
        'refresh'            : function () {
            storageFactory.save_state('role_list', $scope.list_data);
            $scope.list_data.sort_order = $scope.getSortOrder();  //Check if user changed sort order
            $scope.loading = 1;
            roleFactory.getRoles(
                $scope.list_data.page,
                $scope.list_data.selected_categories,
                $scope.list_data.results_per_page,
                $scope.list_data.sort_order,
                $scope.list_data.list_filter,
                $scope.list_data.reverse
                )
                .success(function (data) {
                    $scope.roles = data['results'];

                    $scope.list_data.page = parseInt(data['cur_page']);
                    $scope.list_data.num_pages = parseInt(data['num_pages']);

                    // Bug in API causes it to not return `cur_page` or `num_pages` when less than a single page of data in database
                    // This causes the query to be cached with null values, which means subsequent requests return no data
                    // Defaulting these values to 1 ensures we never cache the query with null values
                    $scope.list_data.page = $scope.list_data.page || 1;
                    $scope.list_data.num_pages = $scope.list_data.num_pages || 1;


                    $scope.num_roles = parseInt(data['count']);
                    $scope.list_data.page_range = [];
    
                    $scope.setPageRange();
    
                    $scope.status = "";
                    storageFactory.save_state('role_list', $scope.list_data);
                    $scope.loading = 0;
    
                    // Force window back to the top
                    window.scrollTo(0, 0);
                    })
                .error(function (error) {
                    $scope.roles = [];
                    $scope.list_data.page = 1;
                    $scope.list_data.num_pages = 1;
                    $scope.list_data.page_range = [1];
                    $scope.num_roles = 0;
                    $scope.status = 'Unable to load roles list: ' + error.message;
                    $scope.loading = 0;
                    });
            }

        };
 
    $scope.page_range = [1];
    $scope.categories = [];
    $scope.roles = [];
    $scope.num_roles = 0;
    $scope.status = '';

    $scope.loading = 0;
    $scope.viewing_roles = 1;
    $scope.display_user_info = 1;
    
    PaginateInit({ scope: $scope });

    $scope.getCategories = function () {
        categoryFactory.getCategories('name',true)
            .success( function (data) {
                $scope.categories = data;
                var tags = [];
                for (var i=0; i < data.length; i++) {
                    tags.push(data[i].name);
                }
                $scope.tags = tags;
                $('#categories-select').select2({
                    width: '100%',
                    tags: tags,
                    placeholder: 'Categories',
                    tokenSeparators: [",", " "]
                    });
                $('#categories-select').on('change', function() { $scope.change_category() });
                if ($scope.list_data.selected_categories.length > 0) {
                    $('#categories-select').val($scope.list_data.selected_categories).trigger('change');
                }
                })
            .error( function (error) {
                  
                  // ERROR HANDLING!!! 

                });
            };

    $scope.is_selected = function(item) {
        if ($scope.list_data.selected_categories.indexOf(item) != -1)
            return true;
        else 
            return false;
        }
    
    // Category field tag change
    $scope.change_category = function() {
        $scope.list_data.selected_categories = $('#categories-select').select2('val');
        $scope.list_data.refresh();
        }

    // User clicked on a tag link.
    $scope.pick_category = function(val) {
        var tags = '';
        var found = false; 
        for (var i=0; i < $scope.list_data.selected_categories.length; i++) {
            if ($scope.list_data.selected_categories[i] == val) {
               found = true;
               break;
            }
        }
        if (!found) {
           $scope.list_data.selected_categories.push(val);
           $('#categories-select').val($scope.list_data.selected_categories).trigger("change");
        }
        }

    $scope.toggle_reverse = function() {
        $scope.list_data.reverse = !$scope.list_data.reverse;
        $scope.list_data.refresh();
        }

    $scope.toggle_category = function(item) {
        var pos = $scope.list_data.selected_categories.indexOf(item);
        if (pos != -1) {
            $scope.list_data.selected_categories.splice(pos, 1);
        } else {
            $scope.list_data.selected_categories.push(item)
        }
        $location.path('roles');
        $scope.list_data.refresh();
        }

    $scope.clear_categories = function() {
        $location.path('roles');
        $scope.list_data.selected_categories = [];
        $scope.list_data.page = 1;
        $scope.list_data.refresh();
        }
    
    $scope.list_data = storageFactory.restore_state('role_list', $scope.list_data);

    if ($routeParams.category_name) {
        $scope.list_data.selected_categories = [$routeParams.category_name];
    }

    if ($routeParams.sort_order) {
        switch ($routeParams.sort_order) {
            case 'sort-by-community-score':
                $scope.list_data.sort_order = 'average_score,name';
                $scope.list_data.reverse = true;
                break;
            case 'sort-by-created-on-date':
                $scope.list_data.sort_order = 'created';
                $scope.list_data.reverse = true;
                break;          
        }
    }

    SearchInit({ 
        scope: $scope,
        placeHolder: 'Search role name',
        showSearchIcon: ($scope.list_data.list_filter) ? false : true,
        sortOptions: [
            { value: 'name', label: 'Role Name' },
            { value: 'owner__username,name', label: 'Owner Name' },
            { value: 'average_score,name', label: 'Average Score' },
            { value: 'created', label: 'Create On Date' }
            ],
        sortOrder: $scope.list_data.sort_order
        });

    $scope.getCategories();
    $scope.list_data.refresh();
    }
    ]);

listControllers.controller('RoleDetailCtrl', ['$q', '$scope','$routeParams','$location','$modal', '$compile', 'roleFactory','userFactory','ratingFactory',
'meFactory', 'relatedFactory', 'my_info', 'Stars', 'PaginateInit',
function($q, $scope, $routeParams, $location, $modal, $compile, roleFactory, userFactory, ratingFactory, meFactory, relatedFactory, my_info, Stars, PaginateInit) {
    
    $scope.page_title = 'Role Detail';
    $scope.showRoleName = false; 
    $scope.my_info = my_info;

    $scope.list_data = {
        'ratings' : {
            'list_filter'        : '',
            'num_pages'          : 1,
            'page'               : 1,
            'results_per_page'   : 10,
            'reverse'            : false,
            'selected_categories': [],
            'sort_order'         : 'created',
            'refresh'            : function() {
                $scope.$emit('getRelated', 'ratings', $scope.role.related.ratings);
                }
            }
        };

    function getLabel(itm) {
        var label;
        switch(itm) {
            case "avg_wow_factor":
                label="Wow! Factor";
                break; 
            case "avg_documentation":
                label="Documentation";
                break; 
            case "avg_reliability": 
                label="Reliability";
                break;
            case "avg_code_quality":
                label="Code Quality";
                break;
            case "average_score":
                label="Community Score";
                break;
            case "average_aw_score":
                label="Ansible Score";
                break;
        }
        return label;  
    }

    $scope.role = {num_ratings: 0};
    $scope.ratings = [];
    $scope.display_user_info = 1;

    PaginateInit({'scope': $scope});

    /* Inject HTML for ratings after the role data is available. Putting HTML in the template prior to having
       values for rating-states attribute causes an error, where the TB-UI rating directive fires and encounters
       a non-array value. So to prevent that we need to make sure it fires after the data is available */
    if ($scope.removeInsertRatings) {
        $scope.removeInsertRatings();
    }
    $scope.removeInsertRatings = $scope.$on('insertRatings', function(e, data, setName) {
        // Insert HTML for rating widget after the data is ready
        var html = '<table>\n<tbody>\n';
        var set = data[setName];
        var score = (setName == 'average_composite') ? 'average_score' : 'average_aw_score';
        set[score] = data[score];  //push the score into the set, so it gets stars 

        var k=0;
        for (var itm in set) {
            k++;
            var itm_value = parseFloat(set[itm]);

            // Use the following to test actual floating points and create 1/2 stars 
            //itm_value += (k*2) / 10;
            //data[setName][itm] = itm_value;
            
            $scope[setName + '_' + itm + '_ceil'] = Math.ceil(itm_value);
            $scope[setName + '_' + itm + '_states'] = [];
            for (var i=0; i < Math.floor(itm_value); i++) {
                $scope[setName + '_' + itm + '_states'].push({ stateOn: 'fa fa-star', stateOff: 'fa fa-star-o' });
            }
            if (itm_value % 1 > 0) {
                $scope[setName + '_' + itm + '_states'].push({stateOn: 'fa fa-star-half-o', stateOff: 'fa fa-star-half-o' });   
            }
            // Fill in missing stars with empties
            for (var i=$scope[setName + '_' + itm + '_states'].length; i < 5; i++) {
                $scope[setName + '_' + itm + '_states'].push({stateOn: 'fa fa-star-o' });
            }
        }

        var label = getLabel(score);
        html += "<tr class=\"primary-score\"><td ng-mouseenter=\"startHover('" + setName + "', '" + score + "')\" " +
                "ng-mouseleave=\"stopHover('" + setName + "', '" + score + "')\">" + label + "</td>\n";
        html += "<td><rating value=\"5\" readonly=\"true\" rating-states=\"" + setName + "_" + score + "_states" + "\" " +
            "on-hover=\"startHover('" + setName + "', '" + score + "')\" on-leave=\"stopHover('" + setName + "', '" + score + "')\"></rating>\n";
        html += "<span class=\"badge\" ng-show=\"" + setName + '_' + score + '_over' + "\">{{ role" + '.' + score + " | number:1 }}</span>\n";
        html += "</td></tr>\n";
        delete set[score];

        for (var itm in set) {
            label = getLabel(itm);
            html += "<tr><td ng-mouseenter=\"startHover('" + setName + "', '" + itm + "')\" " +
                "ng-mouseleave=\"stopHover('" + setName + "', '" + itm + "')\">" + label + "</td>\n";
            
            html += "<td><rating value=\"5\" readonly=\"true\" rating-states=\"" + setName + "_" + itm + "_states" + "\" " +
                "on-hover=\"startHover('" + setName + "', '" + itm + "')\" on-leave=\"stopHover('" + setName + "', '" + itm + "')\"></rating>\n";
            
            html += "<span class=\"badge\" ng-show=\"" + setName + '_' + itm + '_over' + "\">{{ role." + setName + '.' + itm + " | number:1 }}</span>\n";
            html += "</td></tr>\n";       
        }
        html += "</tbody>\n</table>\n";
        set[score]
        var element = angular.element(document.getElementById(setName + '_breakdown'));
        element.html(html);
        $compile(element)($scope);
        });

    $scope.startHover = function(set, itm) {
        $scope[set + '_' + itm + '_' + 'over'] = true; 
        }

    $scope.stopHover = function(set, itm) {
        $scope[set + '_' + itm + '_' + 'over'] = false; 
        }

    $scope.ratingHover = function(itm, label, flag) {
        $scope[label + '_' + 'hover' + '_' + itm] = flag; 
        }

    $scope.getRole = function() { 
        roleFactory.getRole($routeParams.role_id)
            .success( function(data) {
                $scope.role = data;
                $scope.$emit('insertRatings', data, 'average_composite');
                $scope.$emit('insertRatings', data, 'average_aw_composite');
                $scope.$emit('getRelated', 'ratings', data.related.ratings);
                })
            .error( function(error) {
                $scope.status = 'Unable to load role: ' + error.message;
                });
        }

    $scope.addVote = function(id, direction) {
        ratingFactory.addVote(id, {'id':my_info.id}, direction)
            .success( function(data) {
                $scope.$emit('getRelated', 'ratings', $scope.role.related.ratings);
                })
            .error( function(error) {
                //console.error("failed to add a "+direction+" vote on rating id=" + id);
                });
    }

    if ($scope.removeRelated) {
        $scope.removeRelated();
    }
    $scope.removeRelated = $scope.$on('getRelated', function(e, target, url) {
        $scope.list_data[target].url = url;  
        relatedFactory.getRelated($scope.list_data[target])
            .success( function(data) {
                $scope.list_data[target].page = parseInt(data['cur_page']);
                $scope.list_data[target].num_pages = parseInt(data['num_pages']);
                $scope.list_data[target].page_range = [];
                $scope.setPageRange(target);

                // Add 'ranges' to the data that we can pipe through ng-repeat to create a graphic
                // representation of each rating.
                for (var i=0; i < data['results'].length; i++) {
                    data['results'][i].reliability_range = Stars(data['results'][i].reliability);
                    data['results'][i].documentation_range = Stars(data['results'][i].documentation);
                    data['results'][i].code_quality_range = Stars(data['results'][i].code_quality);
                    data['results'][i].wow_factor_range = Stars(data['results'][i].wow_factor);
                    data['results'][i].score_range = Stars(data['results'][i].score);    
                }
                $scope[target] = data['results'];
                })
            .error(function (error) {
                $scope.status = 'Unable to load related '+target+': ' + error.message;
                });
        });

    var ModalInstanceCtrl = function ($scope, $modalInstance, role, ratingFactory, rating) {
        $scope.alerts = [];
        $scope.role = role;
        if (rating) {
            $scope.rating = rating;
        } 
        else {
            $scope.rating = {
                'reliability': 0, 
                'documentation': 0, 
                'code_quality': 0, 
                'wow_factor': 0, 
                'comment': '', 
                }
        }

        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
            };

        $scope.ok = function () {
            if ($scope.rating.reliability == 0 ||
                $scope.rating.documentation == 0 ||
                $scope.rating.code_quality == 0 ||
                $scope.rating.wow_factor == 0 ) {
                    $scope.alerts = [{type: 'danger','msg':'You must choose a rating for each category'}]
                    return;
                }
            var post_data = {
                'pk': $scope.role.id,
                }
            angular.extend(post_data, $scope.rating);
            ratingFactory.addRating(
                role.related.ratings, 
                post_data
                )
                .success(function(data) {
                    $modalInstance.close(true);
                    })
                .error(function(data, status) {
                    var msg = '';
                    console.log(status);
                    if (status == 403) {
                        msg = 'You do not have permission to add a rating to this role.';
                    } else if(status == 409) {
                        msg = 'You appear to have already rated this role. If your rating is not visible, it may mean that an administrator has removed it for violating our terms of service. If you believe this was done in error, please contact us.';
                    } else {
                        msg = 'An unknown error occurred while trying to add your rating. Please wait a while and try again.';
                    }
                    $scope.alerts = [{type: 'danger','msg':msg}]
                    });
            };

        $scope.cancel = function () {
            $modalInstance.dismiss('cancel');
            };
        }

    $scope.showRatingDialog = function() {
        if (!my_info.authenticated) return;
        
        var modalInstance = $modal.open ({
            templateUrl: "/static/partials/add-rating.html",
            controller: ModalInstanceCtrl,
            resolve: {
                role: function() { return $scope.role; },
                ratingFactory: function() { return ratingFactory; },
                rating: function() {
                    var d = $q.defer();
                    ratingFactory.getMyRatingForRole(my_info.id, $scope.role.id)
                        .success(function (data) {
                            if (data.count > 0) {
                                // it should never be > 1, but we only
                                // care the first result anyway
                                var res = angular.copy(data['results'][0]);
                                var rating = {
                                    'id': res.id,
                                    'reliability': parseInt(res.reliability),
                                    'documentation': parseInt(res.documentation),
                                    'code_quality': parseInt(res.code_quality),
                                    'wow_factor': parseInt(res.wow_factor),
                                    'comment': res.comment
                                    }
                                d.resolve(rating);
                            } 
                            else {
                                d.resolve(null);
                            }
                            })
                        .error(function (error) {
                            d.reject(error);
                            });
                    return d.promise;
                    }
                }
            });

        modalInstance.result.then(function (result) {
            if (result) {
                $scope.getRole();
                }
            });
        };

    $scope.staffDeleteRating = function(id) {
            ratingFactory.deleteRating(id)
            .success(function (data) {
                $scope.getRole();
            })
            .error(function (error) {
                alert("Failed to remove rating "+id+", reason: "+error);
            });
        };

    $scope.staffDeleteRole = function(id) {
            roleFactory.deleteRole(id)
            .success(function (data) {
                $location.path('/roles');
            })
            .error(function (error) {
                alert("Failed to remove role "+id+", reason: "+error);
            });
        };

    $scope.getRole();
    }
    ]);


listControllers.controller('UserListCtrl', ['$scope','$timeout','$location','$routeParams', 'userFactory','storageFactory','my_info', 'SearchInit',
'PaginateInit', 'Stars',
function($scope, $timeout, $location, $routeParams, userFactory, storageFactory, my_info, SearchInit, PaginateInit, Stars) {
      
    $scope.page_title = 'Browse Users';
    $scope.my_info = my_info; 

    $scope.list_data = {
        'list_filter'        : '',
        'num_pages'          : 1,
        'page'               : 1,
        'results_per_page'   : 10,
        'reverse'            : false,
        'selected_categories': [],
        'sort_order'         : 'username',
        'refresh'            : function() {
            storageFactory.save_state('user_list', $scope.list_data);
            $scope.list_data.sort_order = $scope.getSortOrder();
            console.log("sort order is " + $scope.list_data.sort_order);
            $scope.loading = 1;
            userFactory.getUsers(
                $scope.list_data.page,
                $scope.list_data.results_per_page,
                $scope.list_data.sort_order,
                $scope.list_data.reverse,
                $scope.list_data.list_filter
                )
                .success( function (data) {
                    for (var i=0; i < data['results'].length; i++) {
                        data['results'][i].karma_range = Stars(data['results'][i].karma);
                        data['results'][i].avg_rating_range = Stars(data['results'][i].avg_rating);
                        data['results'][i].avg_role_score_range = Stars(data['results'][i].avg_role_score);
                        data['results'][i].avg_role_aw_score_range = Stars(data['results'][i].avg_role_score);
                        if (data['results'][i].summary_fields.ratings.length > 0) {
                            data['results'][i].rating_range = Stars(data['results'][i].summary_fields.ratings[0].score);
                        }
                        else {
                            data['results'][i].rating_range = Stars(0);
                        }
                    }
                    if (data['results'].length) {
                        $scope.users = angular.copy(data['results']);
                    }
                    $scope.list_data.page = parseInt(data['cur_page']);
                    $scope.list_data.num_pages = parseInt(data['num_pages']);
                    $scope.num_users = parseInt(data['count']);
                    $scope.list_data.page_range = [];
                    
                    $scope.setPageRange();
                    
                    $scope.status = "";
                    storageFactory.save_state('user_list', $scope.list_data);
                    $scope.loading = 0;

                    // Force window back to the top
                    window.scrollTo(0, 0);
                    })
                .error(function (error) {
                    $scope.users = [];
                    $scope.num_users = 0;
                    $scope.list_data.page = 1;
                    $scope.list_data.num_pages = 1;
                    $scope.list_data.page_range = [1];
                    $scope.status = 'Unable to load users list: ' + error.message;
                    $scope.loading = 0;
                    });
            }
        };
  
    $scope.page_range = [1];
    $scope.categories = [];
    $scope.users = [];
    $scope.num_users = 0;
    $scope.status = '';
    
    $scope.loading = 0;
    $scope.viewing_users = 1;

    PaginateInit({ scope: $scope });

    $scope.hover = function(idx, fld, val) {
        $scope[fld + '_hover_' + idx] = val;
        }

    $scope.toggle_reverse = function() {
        $scope.list_data.reverse = !$scope.list_data.reverse;
        $scope.list_data.refresh();
        };

    $scope.list_data = storageFactory.restore_state('user_list', $scope.list_data);
    
    if ($routeParams.sort_order) {
        switch ($routeParams.sort_order) {
            case 'sort-by-community-score':
                $scope.list_data.sort_order = 'avg_role_score,username';
                $scope.list_data.reverse = true;
                break;
            case 'sort-by-joined-on-date':
                $scope.list_data.sort_order = 'date_joined,username';
                $scope.list_data.reverse = true;
                break;
            case 'sort-by-top-reviewers': 
                $scope.list_data.sort_order = 'karma,username';
                $scope.list_data.reverse = true;
                break;      
        }
    }
    
    SearchInit({ 
        scope: $scope,
        placeHolder: 'Search user',
        showSearchIcon: ($scope.list_data.list_filter) ? false : true,
        sortOptions: [
            { value: 'username', label: 'Username' },
            { value: 'karma,username', label: 'Karma Score' },
            { value: 'avg_role_score,username', label: 'Average Role Score' },
            { value: 'num_roles,username', label: 'Number of Roles' },
            { value: 'date_joined,username', label: 'Date Joined' }
            ],
        sortOrder: $scope.list_data.sort_order
        });

    $scope.list_data.refresh();

    }
    ]);


listControllers.controller('UserDetailCtrl', ['$scope','$routeParams','$location','userFactory','ratingFactory','my_info', 'Range', 'relatedFactory', 'Empty',
'Stars','PaginateInit',
function($scope, $routeParams, $location, userFactory, ratingFactory, my_info, Range, relatedFactory, Empty, Stars, PaginateInit) {

    $scope.my_info = my_info;
    $scope.page_title = 'User Detail';
    $scope.showRoleName = true; 
    $scope.my_info = my_info; 

    $scope.list_data = {
        'roles' : {
            'list_filter'        : '',
            'num_pages'          : 1,
            'page'               : 1,
            'results_per_page'   : 10,
            'reverse'            : false,
            'selected_categories': [],
            'sort_order'         : 'name',
            'refresh'            : function() {
                $scope.$emit('refreshRelated', 'roles', $scope.user.related.roles);
                }
            },
        'ratings' : {
            'list_filter'        : '',
            'num_pages'          : 1,
            'page'               : 1,
            'results_per_page'   : 10,
            'reverse'            : true,
            'selected_categories': [],
            'sort_order'         : 'created',
            'refresh'            : function() {
                $scope.$emit('refreshRelated', 'ratings', $scope.user.related.ratings);
                }
            }
        };

    $scope.user = {'num_roles':0, 'num_ratings':0};
    $scope.roles = [];
    $scope.ratings = [];
   
    PaginateInit({ scope: $scope });
 
    // controls whether or not the role info
    // is displayed in the -display partials
    $scope.display_role_info = 1;
    $scope.display_user_info = 0;

    $scope.getUser = function() {
        userFactory.getUser(
            $routeParams.user_id
            )
            .success(function (data) {
                $scope.user = data;
                $scope.list_data.roles.refresh();
                $scope.list_data.ratings.refresh();
                })
            .error(function (error) {
                $scope.status = 'Unable to load user: ' + error.message;
                });
        };

    $scope.ratingHover = function(itm, label, flag) {
        $scope[label + '_' + 'hover' + '_' + itm] = flag; 
        }

    $scope.addVote = function(id, direction) {
        ratingFactory.addVote(id, {'id':my_info.id}, direction)
            .success( function(data) {
                $scope.$emit('refreshRelated', 'ratings', $scope.user.related.ratings);
                })
            .error( function(error) {
                console.error("failed to add a "+direction+" vote on rating id=" + id);
                });
    }
 
    if ($scope.removeRelated) {
        $scope.removeRelated();
    }
    $scope.removeRelated = $scope.$on('refreshRelated', function(e, target, url) {
        $scope.list_data[target].url = url;  
        relatedFactory.getRelated($scope.list_data[target])
            .success( function(data) {
                $scope.list_data[target].page = parseInt(data['cur_page']);
                $scope.list_data[target].num_pages = parseInt(data['num_pages']);
                $scope.list_data[target].page_range = [];
                $scope.setPageRange(target);

                if (data['results'].length > 0 && !Empty(data['results'][0].reliability)) {
                    // Add 'ranges' to the data that we can pipe through ng-repeat to create a graphic
                    // representation of each rating.
                    for (var i=0; i < data['results'].length; i++) {
                        data['results'][i].reliability_range = Stars(data['results'][i].reliability);
                        data['results'][i].documentation_range = Stars(data['results'][i].documentation);
                        data['results'][i].code_quality_range = Stars(data['results'][i].code_quality);
                        data['results'][i].wow_factor_range = Stars(data['results'][i].wow_factor);  
                        data['results'][i].score_range = Stars(data['results'][i].score); 
                    }
                }
                $scope[target] = data['results'];
                })
            .error(function (error) {
                $scope.status = 'Unable to load related ' + target + ': ' + error.message;
                });
        });

    $scope.staffDeleteRating = function(id) {
            ratingFactory.deleteRating(id)
            .success(function (data) {
                $scope.getUser();
            })
            .error(function (error) {
                alert("Failed to remove rating "+id+", reason: "+error);
            });
        };

    $scope.staffDeleteUser = function(id) {
            userFactory.deleteUser(id)
            .success(function (data) {
                $location.path('/users');
            })
            .error(function (error) {
                alert("Failed to remove user "+id+", reason: "+error);
            });
        };

    $scope.getUser();
    
    }
    ]);

