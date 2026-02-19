from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBookManagerOrReadOnly(BasePermission):
    managers_group = "book_managers"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name=self.managers_group).exists()
        )
