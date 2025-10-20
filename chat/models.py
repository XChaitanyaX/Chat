from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    ROOM_CHOICES = (
        ("group", "Group Chat"),
        ("private", "Private Chat"),
    )
    name = models.CharField(max_length=255, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_CHOICES)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def display_name_for(self, user):
        if self.room_type == "group":
            return self.name
        return "".join(
            name for name in self.name.split("_") if name != user.username
        )


class Message(models.Model):
    room_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content
