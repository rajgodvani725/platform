# vendors/models.py
from django.contrib.auth.models import User
from django.db import models
User._meta.get_field('email')._unique = True
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other fields specific to vendors if needed

    def __str__(self):
        return self.user.username


class VendorUser(models.Model):
    VENDOR_ROLES = (
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('salesperson', 'Salesperson'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=VENDOR_ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Store(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,unique=True)
    location = models.CharField(max_length=100)
    contact_details = models.CharField(max_length=100)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'contact_details': self.contact_details
        }
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    available_units = models.IntegerField(default=0) 
    sold_units = models.IntegerField(default=0)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,  
            'manufacturer': self.manufacturer, 
            'price': str(self.price),  
            'available_units': self.available_units,
            'sold_units': self.sold_units,
            'store':self.store.name
        }
    
    def __str__(self):
        return self.name
