from django.http import HttpResponse
import json

class SuccessCommand():
    def doPost(self, request, client):
        response = {
            'SUCCESS': True,
            'MESSAGE': client.response_message,
            'CURSWITCH': request['SWITCH']
        }
        
        return HttpResponse(json.dumps(response), content_type='application/json')

class NotFoundCommand():
    def doPost(self, request, client):
        
        return HttpResponse("Not Found", status=404)

class ErrorCommand():
    def doPost(self, request, client):
        response = {
            'code': 100,
            'message': 'This is a test error message.'
        };
        return HttpResponse(json.dumps(response), status=400, content_type='application/json');

class HangUpCommand():
    def doPost(self, request, client):
        pass
