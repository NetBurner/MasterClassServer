from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.views.generic.base import View, TemplateView
from django.http import HttpResponse
import json
from datetime import datetime, timedelta
from m7site.models import Client, Command, Record
import m7site.commands
from m7site.services import get_clients
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)

def update_client(request):
    request_data = json.loads(request.body)
    
    if 'id' not in request_data:
        response = { 'error': { 'message': 'Key "id" is required.' } }
        return HttpResponse(json.dumps(response), status=400, content_type="application/json")

    client = Client.objects.get(uuid=request_data['id'])
    
    if 'student_name' in request_data: client.student_name = request_data['student_name'] 
    if 'response_message' in request_data: client.response_message = request_data['response_message'] 
    if 'current_command' in request_data:
        command = Command.objects.get(id=request_data['current_command'])
        client.current_command = command

    client.save()
    values = dict(client.__dict__)
    print (values.keys())
    del values['_state']
    del values['last_seen']
    return HttpResponse(json.dumps(values), content_type="application/json")

def get_client_history(request):
    request_data = json.loads(request.body)

    if 'id' not in request_data:
        response = { 'error': { 'messages': ['Key "id" is required.'] } }
        return HttpResponse(json.dumps(response), status=400, content_type="application/json")

    records = Record.objects.filter(uuid = request_data['id'], created_at__gte=datetime.now() - timedelta(minutes=10)).order_by('created_at')
    records_data = []
    for record in records:
        values = dict(record.__dict__)
        del values['_state']
        del values['id']
        values['created_at'] = values['created_at'].isoformat()
        records_data.append(values)

    return HttpResponse(json.dumps(records_data), content_type="application/json")

def reset(request):
    Client.objects.all().delete()
    Record.objects.all().delete()
    return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class ClientView(View):

    def post(self, request, *args, **kwargs):
        # Input Validation
        request_data = json.loads(request.body)
        errors = []
        if 'DEVICEID' not in request_data:
            errors.append("'DEVICEID' must be a key in the submitted document.");
        if 'STUDENTNAME' not in request_data:
            errors.append("'STUDENTNAME' must be a key in the submitted document.");
        if 'MESSAGE' not in request_data:
            errors.append("'MESSAGE' must be a key in the submitted document.");
        if 'UPTIME' not in request_data:
            errors.append("'UPTIME' must be a key in the submitted document.");
        if 'SWITCH' not in request_data:
            errors.append("'SWITCH' must be a key in the submitte document.");
        if len(errors) > 0:
            response = {
                "error": {
                    "messages": errors
                }
            }
            return HttpResponse(json.dumps(response), status=400, content_type="application/json")
       
        # Initialize variables 
        last_seen = datetime.now()
        default_command = Command.objects.get(id=1) # I don't have a good way of establishing an initial value for this given the behavior of of the ORM, and I'm not sure if this accesses the database; it may not.

        # Get or initialize the client
        client, created = Client.objects.get_or_create(
            uuid=request_data['DEVICEID'],
            defaults={
                'student_name': request_data['STUDENTNAME'],
                'current_command': default_command,
                'response_message': 'Welcome',
                'last_seen': last_seen,
                'last_message': request_data['MESSAGE'],
                'last_switch': request_data['SWITCH']})
        if not created:
            client.last_seeen = last_seen
            client.last_message = request_data['MESSAGE']
            client.last_switch = request_data['SWITCH']
            client.student_name = request_data['STUDENTNAME']
            client.save()

        # Add access to the audit trail. I'd like to add this to an asynchronous processing chain, actually, but I don't think Python works that way.
        record = Record(uuid=request_data['DEVICEID'], message=request_data['MESSAGE'], uptime=request_data['UPTIME'], switch=request_data['SWITCH'], created_at=last_seen)
        record.save()

        clients = get_clients()
        async_to_sync(get_channel_layer().group_send)('clients', { 'type': 'client.update' })

        # Invoke command
        command = client.current_command.class_name
        command_class = getattr(m7site.commands, command)
        command_object = command_class()
        response = command_object.doPost(request_data, client)
        
        return response

class AdminView(TemplateView):
    
    template_name = "admin.html"

    def get_context_data(self, **kwargs):
        clients = Client.objects.order_by('student_name')
        commands = Command.objects.all()
        logging.debug("Commands: ")
        for command in commands:
            logging.debug(str(command))
    
        context = super().get_context_data(**kwargs)
        context['clients'] = clients
        context['commands'] = commands
        return context
