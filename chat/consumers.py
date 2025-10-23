import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message


class PrivateChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"private_{self.room_name}"

        if not self.scope["user"].is_authenticated:
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

        # load prev chats
        prev_messages = Message.objects.filter(
            room_name=self.room_name
        ).order_by("timestamp")
        for msg in prev_messages:
            self.send(
                text_data=json.dumps(
                    {"message": msg.content, "username": msg.username},
                )
            )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else "Anonymous"
        )

        Message.objects.create(
            room_name=self.room_name,
            username=username,
            content=message,
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            },
        )

    def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        self.send(text_data=json.dumps({"message": message, "username": username}))
