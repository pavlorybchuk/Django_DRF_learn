from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Manager').exists()
        )


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Delivery crew').exists()
        )


class IsCustomer(BasePermission):
    """
    A user is considered a customer if they are authenticated
    but NOT in Manager or Delivery crew groups.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not request.user.groups.filter(name__in=['Manager', 'Delivery crew']).exists()