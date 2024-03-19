from django.contrib import admin
from .models import Vendor,VendorUser,Store,Product
# Register your models here.
admin.site.register(Vendor)
admin.site.register(VendorUser)
admin.site.register(Store)
admin.site.register(Product)