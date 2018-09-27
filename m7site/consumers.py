from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from m7site.models import Client
from m7site.services import get_clients

class ClientConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("clients", self.channel_name)
        self.client_update({})

    def disconnect(self, close_code):
        pass

    def client_update(self, event):
        self.send(
            json.dumps(get_clients())
        )
