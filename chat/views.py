from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import View
from django.views.decorators.http import require_POST

from chat.models import Message, Room
from chat.utils import create_roomname

from .forms import LoginForm


def index(request):
    rooms = Room.objects.filter(users=request.user)
    history = [room.display_name_for(request.user) for room in rooms]
    return render(request, "chat/index.html", {"history": history})


@require_POST
def room(request, room_name):
    room = Room.objects.get(name=room_name)
    messages = Message.objects.filter(room_name=room.name).order_by(
        "timestamp"
    )
    html = render_to_string(
        "chat/room.html",
        {"room": room, "messages": messages},
    )
    return JsonResponse({"html": html})


class Login(View):
    def get(self, request):
        return render(request, "chat/login.html", {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                form.add_error(None, "Invalid username or password")
        return render(request, "chat/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@require_POST
def add_user(request, username):
    data = {
        "success": False,
        "userid": None,
        "username": None,
    }
    try:
        user = User.objects.get(username=username)
        data["success"] = True
        data["userid"] = user.id
        data["username"] = user.username

        room_name = create_roomname(request.user.username, user.username)
        try:
            room = Room.objects.get(name=room_name, room_type="private")
        except Room.DoesNotExist:
            room = Room.objects.create(name=room_name, room_type="private")
            room.users.add(request.user, user)
    except User.DoesNotExist:
        pass
    return JsonResponse(data)
