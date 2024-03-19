# vendors/views.py
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Vendor, VendorUser, Store, Product
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsVendor, IsAdmin, IsSupervisor,IsSales
from .helpers import create_sales_supervisor
import json

import pandas as pd


@api_view(["POST"])
def register_vendor(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")
        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = User.objects.create_user(username=username, password=password)
        vendor = Vendor.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Vendor registered successfully!",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
    return Response(
        {"error": "Only POST requests are allowed."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsVendor])
def register_user(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role")
        if not role or role == "":
            return Response(
                {"message": "role not provided"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        vendor = Vendor.objects.filter(user=request.user).first()
        if not vendor:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if role == "admin":
            existing_user = User.objects.filter(username=username, password=password)
            if existing_user:
                return Response(
                    {"message": "username already exists"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            user = User.objects.create_user(username=username, password=password)
            vendor_user = VendorUser.objects.create(user=user, vendor=vendor, role=role)
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            create_user_status = create_sales_supervisor(
                username, password, role, vendor
            )
            if create_user_status == 500:
                return Response(
                    {"message": "username already exists"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            else:
                return Response(
                    {"message": "User registered successfully"},
                    status=status.HTTP_201_CREATED,
                )

    return Response(
        {"error": "Only POST requests are allowed."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@api_view(["POST"])
def vendor_login(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                if user.vendor:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "message": "Login successful",
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    )
                else:
                    return Response(
                        {"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                print(e)
                return Response(
                    {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    return Response(
        {"error": "Only POST requests are allowed."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@api_view(["POST"])
def user_login(request):
    if request.method == "POST":
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            try:
                if user.vendoruser:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "message": "Login successful",
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "role": user.vendoruser.role,
                        }
                    )
                else:
                    return Response(
                        {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                print(e)
                return Response(
                    {"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

    return Response(
        {"error": "Only POST requests are allowed."},
        status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def users(request):
    if request.method == "GET":
        vendor = request.user.vendoruser.vendor
        users = VendorUser.objects.filter(
            Q(vendor=vendor, role="supervisor") | Q(vendor=vendor, role="salesman")
        )
        users_data = [{"username": supervisor.user.username} for supervisor in users]
        return Response({"users": users_data}, status=200)
    if request.method == "DELETE":
        vendor = request.user.vendoruser.vendor
        VendorUser.objects.get(
            vendor=vendor, user__username=request.data.get("username")
        ).delete()
        users = VendorUser.objects.filter(
            Q(vendor=vendor, role="supervisor") | Q(vendor=vendor, role="salesman")
        )
        users_data = [{"username": supervisor.user.username} for supervisor in users]
        return Response({"users": users_data}, status=200)
    else:
        return Response({"error": "Only GET requests are allowed."}, status=405)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def stores(request):
    if request.method == "GET":
        vendor = request.user.vendoruser.vendor
        stores = Store.objects.filter(vendor=vendor)
        return Response({"stores": [store.to_dict() for store in stores]}, status=200)

    if request.method == "POST":
        vendor = request.user.vendoruser.vendor
        name = request.data.get("name")
        location = request.data.get("location")
        contact_details = request.data.get("contact_details")
        Store.objects.create(
            vendor=vendor, name=name, location=location, contact_details=contact_details
        )
        stores = Store.objects.filter(vendor=vendor)
        return Response({"stores": [store.to_dict() for store in stores]}, status=200)

    if request.method == "DELETE":
        vendor = request.user.vendoruser.vendor
        name = request.data.get("name")
        Store.objects.get(vendor=vendor, name=name).delete()
        stores = Store.objects.filter(vendor=vendor)
        return Response({"stores": [store.to_dict() for store in stores]}, status=200)
    else:
        return Response({"error": "Method not allowed."}, status=405)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated, IsSupervisor])
def products(request):
    if request.method == "GET":
        vendor = request.user.vendoruser.vendor
        stores = Store.objects.filter(vendor=vendor)
        products = Product.objects.filter(store__vendor=vendor)
        return Response(
            {
                "stores": [store.to_dict() for store in stores],
                "products": [product.to_dict() for product in products],
            },
            status=200,
        )

    if request.method == "POST":
        try:
            vendor = request.user.vendoruser.vendor
            if len(request.data.get("files")) > 0:
                file = request.data.get("files")
                df = pd.read_excel(file)
                for index, row in df.iterrows():
                    if Store.objects.get(name=row.store):

                        Product.objects.create(
                            store=Store.objects.get(name=row.store),
                            name=row.product_name,
                            type=row.type,
                            manufacturer=row.manufacturer,
                            price=row.price,
                            available_units=row.get("available_stock", 0),
                            sold_units=row.get("sold_units", 0),
                        )
                return Response({"msg": "File loaded successfully"}, status=200)
            data = json.loads(request.body)
            store = Store.objects.get(name=data["store"])
            if not store:
                return Response({"error": "Invalid store name."}, status=500)
            product = Product.objects.create(
                store=store,
                name=data["name"],
                type=data["type"],
                manufacturer=data["manufacturer"],
                price=data["price"],
                available_units=data.get("available_units", 0),
                sold_units=data.get("sold_units", 0),
            )

            products = Product.objects.filter(store__vendor=vendor, store=store)
            return Response(
                {"products": [store.to_dict() for store in products]}, status=200
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    if request.method == "DELETE":
        vendor = request.user.vendoruser.vendor
        name = request.data.get("name")
        Store.objects.get(vendor=vendor, name=name).delete()
        stores = Store.objects.filter(vendor=vendor)
        return Response({"stores": [store.to_dict() for store in stores]}, status=200)
    else:
        return Response({"error": "Method not allowed."}, status=405)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsSales])
def sales(request):
    if request.method == "POST":
        try:
            product_name = request.POST.get('product')
            count = request.POST.get("count")
            product = Product.objects.get(name=product_name)
            if not product:
                return Response({"error": "Invalid product name."}, status=500)
            product.sold_units += int(count)            
            product.available_units -= int(count)            
            product.save()
            return Response({"msg": "Sales recorded successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)