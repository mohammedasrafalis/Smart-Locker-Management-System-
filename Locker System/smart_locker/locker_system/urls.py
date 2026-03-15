
from django.contrib import admin
from django.urls import path, include
from locker_system import views  # replace 'locker_system' with your app name
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
TokenObtainPairView,
TokenRefreshView
)
from django.urls import path
from .views import *

urlpatterns = [

path('api/auth/register/', register_view),
path('api/auth/login/', login_view),

path('api/lockers/', lockers),
path('api/lockers/available/', available_lockers),

path('api/reservations/', reserve_locker),

]

urlpatterns = [

path('admin/', admin.site.urls),

path('api/', include('locker_system.api_urls')),

path('api/auth/login/', TokenObtainPairView.as_view()),

path('api/auth/refresh/', TokenRefreshView.as_view()),

]

urlpatterns = [

    # Django Admin
    path('admin/', admin.site.urls),

    # Frontend Pages
    path('', views.home, name='home'),          # index.html
    path('login/', views.login_page, name='login'),    # login.html
    path('register/', views.register_page, name='register'),  # register.html

    # API Endpoints (Django REST Framework)
    path('api/', include('locker_system.api_urls')),   # all APIs: lockers, reservations, auth
    
path('admin/', admin.site.urls),

path('', views.home, name='home'),

path('login/', views.login_page, name='login'),

path('register/', views.register_page, name='register'),

path('api/', include('locker_system.api_urls')),

]
