# vendors/urls.py
from django.urls import path
from .views import register_user,register_vendor,vendor_login,user_login,users,stores,products,sales

urlpatterns = [
    path('register/vendor', register_vendor, name='register_vendor'),
    path('register/user', register_user, name='register_user'),
    path('login/vendor', vendor_login, name='login_vendor'),
    path('login/user', user_login, name='login_user'),
    path('users', users, name='users'),
    path('stores', stores, name='users'),
    path('products', products, name='users'),
    path('sales/add-sell', sales, name='users'),

]
