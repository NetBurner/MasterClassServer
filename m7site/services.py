from m7site.models import Client, Record

def get_clients():
    clients = Client.objects.order_by('student_name')
    client_objects = []
    for client in clients:
        #latest_record = Record.objects.filter(uuid=client.uuid).order_by('-created_at')[0]
        switches = []
        comparator = 1;
        for i in range(0, 8):
            switches.append(0 != client.last_switch & comparator)
            comparator = comparator << 1
        values = dict(client.__dict__)
        del values['_state']
        del values['id']
        del values['last_seen']
        values['switches'] = switches
        client_objects.append(values)
    return client_objects
