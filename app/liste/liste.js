'use strict';

angular.module('myApp.liste', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/liste', {
    templateUrl: 'liste/liste.html',
    controller: 'View1Ctrl'
  });
}])

.controller('View1Ctrl', [function() {

}]);