from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """Anyone may read; only the owner or staff may change an object.

    The view may define get_owner_id(obj) when ownership lives elsewhere
    (e.g. an image owned through its listing); otherwise obj.owner_id is used.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        get_owner_id = getattr(view, "get_owner_id", None)
        owner_id = get_owner_id(obj) if get_owner_id else obj.owner_id
        return owner_id is not None and owner_id == request.user.id
