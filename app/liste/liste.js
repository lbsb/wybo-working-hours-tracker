'use strict';

angular.module('myApp.liste', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/liste', {
    templateUrl: 'liste/liste.html',
    controller: 'View1Ctrl'
  });
}])

.controller('View1Ctrl', [function() {
        //To get the data of the json file
        $http.get('data/logs.json').success(function(data,status){
            $scope.articles=data;
            $scope.status=status;
        }).error(function(data, status) { $scope.data = data || "Request failed"; $scope.status = status;
        });
    }]);