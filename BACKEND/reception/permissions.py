from rest_framework.permissions import BasePermission

class IsDoctorOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        # If role exists directly
        if hasattr(user, "role"):
            return user.role in ["Doctor", "Receptionist"]

        # If role is via staff
        if hasattr(user, "staff") and user.staff:
            return getattr(user.staff, "role", None) in ["Doctor", "Receptionist"]

        return False