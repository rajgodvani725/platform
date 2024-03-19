# vendors/views.py
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from .models import VendorUser
from rest_framework import status
from rest_framework.response import Response

def create_sales_supervisor(username,password,role,vendor):
    existing_user = User.objects.filter(username=username, password=password)
    if existing_user:
        return 500
    user = User.objects.create_user(username=username, password=password)
    vendor_user = VendorUser.objects.create(user=user, vendor=vendor, role=role)
    return 201