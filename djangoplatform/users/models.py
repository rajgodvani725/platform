from django.db import models
from django.contrib.auth.models import User
from django.db import models
# Create your models here.
class Customers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other fields specific to vendors if needed

    def __str__(self):
        return self.user.username