'use strict';

angular.module('myApp.liste', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/liste', {
    templateUrl: 'liste/liste.html',
    controller: 'View1Ctrl'
  });
}])

.controller('View1Ctrl', ['$scope','$http', function($scope,$http) {
        //To get the data of the json file
        $http.get('data/users.json').success(function(data,status){
            $scope.users=data;
            $scope.status=status;
        }).error(function(data, status) { $scope.data = data || "Request failed"; $scope.status = status;
        });
    }])
    .controller('DetailCtrl', ['$scope','$http', function($scope,$http) {
        //To get the data of the json file
        $http.get('data/detail.json').success(function(detailData,status){
            $scope.details=detailData;
            $scope.status=status;
        }).error(function(detailData, status) { $scope.detailData = detailData || "Request failed"; $scope.status = status;
        });
    }]);

