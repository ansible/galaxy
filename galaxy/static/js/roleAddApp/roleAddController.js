/*
 * roleAddController.js
 *
 * (c) 2012-2015, Ansible, Inc.
 *
 */


'use strict';

(function(angular) {
    
    var mod = angular.module('roleAddController', []);

    mod.controller('RoleAddCtrl', ['$scope', _controller]);

    function _controller($scope) {
        var urlPattern = new RegExp('^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$');

        $scope.form = {
            githubUrl: null,
            githubUrlLabel: "HTTPS Clone URL",
            githubUrlPlaceholder: "HTTPS Clone URL",
            githubUrlLabelShow: false,
            githubUrlPattern: urlPattern,
            githubUrlChange : _githubUrlChange,
            namespace: null,
            namespaceLabel: "Github User or Organization",
            namespacePlaceholder: "Github user or organization",
            namespaceLabelShow: false,
            repo: null,
            repoLabel: "Github Repository Name",
            repoPlaceholder: "Github Repository Name",
            repoLabelShow: false,
            fieldFocus: _fieldFocus,
            fieldBlur : _fieldBlur
        };

        return;

        var backupPlaceholder = null;

        function _fieldFocus(_field) {
            $scope.form[_field + 'LabelShow'] = true;
            backupPlaceholder = $scope.form[_field + 'Placeholder'];
            $scope.form[_field + 'Placeholder'] = null;
        }

        function _fieldBlur(_field) {
            $scope.form[_field + 'LabelShow'] = false;
            $scope.form[_field + 'Placeholder'] = backupPlaceholder;
        }

        function _githubUrlChange() {
            if ($scope.form.githubUrl) {
                var url = $scope.form.githubUrl.replace('https://','');
                var parts = url.split('/');
                if (parts.length == 3) {
                    $scope.form.namespace = parts[1];
                    $scope.form.repo = parts[2];
                }
            }
        }
    }

})(angular);
 

