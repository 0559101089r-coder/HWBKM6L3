from rest_framework import permissions

class IsAuthenticatedOrReadOnlyCustom(permissions.BasePermission):
    """
    Разрешает безопасные методы (GET, HEAD, OPTIONS) всем, 
    а изменять/создавать данные — только авторизованным пользователям.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        
        return bool(request.user and request.user.is_authenticated)