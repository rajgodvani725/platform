# vendors/permissions.py
from rest_framework import permissions

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'vendor')
    
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'vendoruser') and request.user.vendoruser.role ==  'admin'
    
class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'vendoruser') and request.user.vendoruser.role ==  'supervisor'
    
class IsSales(permissions.BasePermission):
    def has_permission(self, request, view):
        import pdb;pdb.set_trace()
        return request.user.is_authenticated and hasattr(request.user, 'vendoruser') and request.user.vendoruser.role ==  'salesperson'