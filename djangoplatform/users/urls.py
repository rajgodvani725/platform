# vendors/urls.py
from django.urls import path
from .views import register,login

urlpatterns = [
    path('register', register, name='register_vendor'),
    path('login', login, name='login_vendor'),
]
