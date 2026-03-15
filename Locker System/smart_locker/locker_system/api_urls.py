# locker_system/api_urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/register/', views.RegisterUserView.as_view(), name='register'),
    path('auth/login/', views.LoginAPI.as_view(), name='login'),

    # Lockers
    path('lockers/', views.LockerListCreateView.as_view(), name='locker_list'),
    path('lockers/<int:pk>/', views.LockerDetailView.as_view(), name='locker_detail'),
    path('lockers/available/', views.AvailableLockersView.as_view(), name='available_lockers'),
    path('reservations/', views.reserve_locker, name='create_reservation'),
    path('reservations/<int:pk>/release/', views.release_locker, name='release_locker'),
    path('my-reservations/', views.user_reservations, name='user_reservations'),
]