from django.urls import path

from hosts.views import RegisterHostView, RegisterRoomView

urlpatterns = [
    path('', RegisterHostView.as_view()),
    path('/rooms', RegisterRoomView.as_view())
]