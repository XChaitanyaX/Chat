from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/private/chat/(?P<room_name>\w+)/$",
        consumers.PrivateChatConsumer.as_asgi(),
    ),
]
