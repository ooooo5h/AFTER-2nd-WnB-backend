from django.urls import path

from hosts.views import RegisterHostView

urlpatterns = [
    path('', RegisterHostView.as_view())
]