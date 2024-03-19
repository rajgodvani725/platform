# vendors/views.py
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Customers
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
import re
from django.db.models import Q
# Create your views here.
from django.contrib.auth import authenticate

@api_view(["POST"])
def register(request):
    if request.method == "POST":
        data = request.data
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        username= data.get('username')
        try:
            validate_email(email)
        except ValidationError as e:
            return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        if not first_name.isalpha():
            return Response({'error': 'First name can contain only alphabets'}, status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^([a-zA-Z]*(\'[a-zA-Z]*)?)?(\.[a-zA-Z]*)?$', last_name):
             return Response({'error': 'Invalid last name format'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8 or len(password) > 12:
            return Response({'error': 'Password must be between 8 and 12 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        if not any(char.isupper() for char in password):
            return Response({'error': 'Password must contain at least one uppercase letter'}, status=status.HTTP_400_BAD_REQUEST)
        if not any(char.isdigit() for char in password):
            return Response({'error': 'Password must contain at least one digit'}, status=status.HTTP_400_BAD_REQUEST)
        if not any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]|\\~" for char in password):
            return Response({'error': 'Password must contain at least one special character'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Create the user
            user = User.objects.filter(Q(username=username) | Q(email=email))
            if user:
                return Response({'error': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(username=username,email=email, first_name=first_name, last_name=last_name, password=password)
            customer = Customers.objects.create(user=user)
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(["POST"])
def login(request):
    username_or_email = request.data.get('username_or_email')
    password = request.data.get('password')
    if '@' in username_or_email:
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username  # Get the username from the user object
        except User.DoesNotExist:
            return Response({'error': "User doesn't exists"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        username = username_or_email
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "message": "successfully logged in"
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
