(function() {
'use strict';

var app = angular.module('m7site', ['ngMaterial']);

// Source from https://stackoverflow.com/questions/27234110/blur-an-input-field-on-keypress-enter-on-angular
app.directive('nbEnter', function() {
    return function(scope, element, attrs) {
        element.bind("keydown keypress", function(event) {
            if(event.which == 13) {
                scope.$apply(function(){
                    scope.$eval(attrs.nbEnter, { 'event': event } );
                    event.target.blur();
                });
            }
        });
    };
});

app.controller('AdminCtrl', function($scope, $http, $mdDialog) {
    $http.defaults.xsrfCookieName = 'csrftoken';
    $http.defaults.xsrfHeaderName = 'X-CSRFToken';
    $scope.activeStudent = null;
    $scope.students = [];
    var studentDict = {};

    var clientSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/client/'
    );
    clientSocket.onclose = function(e) {
        console.log("Closed.");
    }
    clientSocket.onmessage = function(e) {
        $scope.$apply(function() {
            var data = JSON.parse(e.data);
            $scope.students = [];
            data.forEach(function(newStudent) {
                var student = {};
                if(studentDict[newStudent.uuid] == null) {
                    studentDict[newStudent.uuid] = student;
                } else {
                    student = studentDict[newStudent.uuid];
                }
                ingestStudent(student, newStudent);
                $scope.students.push(student);
            });
        });
    }

    $scope.onStudentClick = function(student, index) {
        //delete student['history'];
        if($scope.activeStudent == student) {
            $scope.activeStudent = null;
        } else {
            $scope.activeStudent = student;
            //$http.post(
                //'/admin/getClientHistory',
                //{
                    //id: student.id
                //}
            //).then(function(response) {
                //$scope.activeStudent.history = response.data;
                /*
                var chartData = [['Device', 'Label', {type: 'string', role: 'tooltip', p: {'html': true} }, 'Time Start', 'Time End' ]];
                response.data.forEach(function(item) {
                    chartData.push([ item.uuid, '', "<p>Message: " + item.message + "</p><p>Switch: " + item.switch + "</p>", new Date(item.created_at), new Date((new Date(item.created_at)).getTime() + 10*1000) ]);
                });
                var data = google.visualization.arrayToDataTable(chartData);
                var currentTime = new Date();
                var minTime = new Date( (new Date()).getTime() - (10 * 60 * 1000) );
                var options = {
                    title: 'History',
                    tooltip: {isHtml: true },
                    legend: { position: 'bottom' },
                    hAxis: {
                        maxValue: currentTime,
                        minValue: minTime
                    }
                };

                var chart = new google.visualization.Timeline(document.getElementById('history_chart'));

                chart.draw(data, options);
                */
            //});
        }
    };
    $scope.commands = commands;

    $scope.onMessageChange = function(student) {
        $http.post(
            "/admin/updateClient",
            {
                id: student.id,
                response_message: student.message
            }
        ).then(function(response) {
            ingestStudent(student, response.data);
        });
    }

    $scope.onCommandChange = function(student, command) {
        student.command = command.id;
        $http.post(
            "/admin/updateClient",
            {
                id: student.id,
                current_command: command.id
            }
        ).then(function(response) {
            ingestStudent(student, response.data);
        }); 
    };
    
    $scope.onClickReset = function(event) {
    	var confirm = $mdDialog.confirm()
    		.title('Are you sure you want to reset the database?')
    		.textContent('This will probably destroy a lot of stuff.')
    		.ariaLabel('Label')
    		.ok('Ok')
    		.cancel('Never mind');
    	$mdDialog.show(confirm).then(function() {
    		return $http.post(
    				"/admin/reset"
    		);
    	}).then(function(response) {
			$scope.students = [];
			$scope.activeStudent = null;
		});
    }

    function ingestStudent(localStudent, remoteStudent) {
        localStudent.id = remoteStudent.uuid;
        localStudent.name = remoteStudent.student_name;
        localStudent.command = remoteStudent.current_command_id;
        localStudent.message = remoteStudent.response_message;
        localStudent.lastMessage = remoteStudent.last_message;
        localStudent.switches = remoteStudent.switches;
    }
});
})();
