from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("add_user/<str:username>/", views.add_user, name="add_user"),
    path("room/<str:room_name>/", views.room, name="room"),
]
