from django.contrib import admin
from django.urls import path, include
from locker_system import views

urlpatterns = [
    path('api/', include('locker_system.api_urls')),
    path('', views.home, name='home'),

    # Legacy / direct file requests (redirects to proper URL patterns)
    path('login.html', views.login_page, name='login_html'),
    path('register.html', views.register_page, name='register_html'),

    path('login/', include([
        path('', views.login_page, name='login'),
        path('register/', views.register_page, name='register'),
    ])),
    path('user/', views.user_page, name='user'),
    path('admin/', views.admin_page, name='admin'),
]

