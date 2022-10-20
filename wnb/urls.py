from django.urls import path, include

urlpatterns = [
    path('users', include('users.urls')),
    path('reservations', include('reservations.urls')),
    path('rooms', include('rooms.urls')),
    path('hosts', include('hosts.urls'))
]