"""
Permisos DRF basados en rol. Se verifican SIEMPRE en el backend.

Uso en una vista:
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]
"""
from rest_framework.permissions import BasePermission

from .models import Role


class _RolePermission(BasePermission):
    allowed_roles: tuple = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active and user.role in self.allowed_roles)


class IsAdmin(_RolePermission):
    allowed_roles = (Role.ADMIN,)


class IsAdminOrSupervisor(_RolePermission):
    allowed_roles = (Role.ADMIN, Role.SUPERVISOR)


class IsCollector(_RolePermission):
    allowed_roles = (Role.COLLECTOR,)


class IsAnyStaffRole(_RolePermission):
    allowed_roles = (Role.ADMIN, Role.SUPERVISOR, Role.COLLECTOR)
