from django.contrib.auth.models import User
from .models import UserPermission

def user_has_permission(user, content_type, permission_type, category=None):
    """
    Check if a user has a specific permission for a content type
    
    Args:
        user: The user to check permissions for
        content_type: 'article', 'category', or 'user'
        permission_type: 'view', 'create', 'edit', 'delete', 'publish', or 'full'
        category: Optional Category object to check category-specific permissions
        
    Returns:
        bool: True if user has permission, False otherwise
    """
    if user.is_superuser:
        return True
        
    # Check for 'full' permission first (gives all access)
    has_full_access = UserPermission.objects.filter(
        user=user,
        content_type=content_type,
        permission_type='full',
        category=category
    ).exists()
    
    if has_full_access:
        return True
    
    # Check for specific permission
    has_permission = UserPermission.objects.filter(
        user=user,
        content_type=content_type,
        permission_type=permission_type,
        category=category
    ).exists()
    
    # If category is specified and no permission found, check for global permission
    if category and not has_permission:
        has_global_permission = UserPermission.objects.filter(
            user=user,
            content_type=content_type,
            permission_type__in=[permission_type, 'full'],
            category__isnull=True
        ).exists()
        
        return has_global_permission
    
    return has_permission

def get_user_permitted_categories(user, permission_type):
    """
    Get all categories a user has a specific permission for
    
    Args:
        user: The user to check permissions for
        permission_type: 'view', 'create', 'edit', 'delete', 'publish', or 'full'
        
    Returns:
        QuerySet: Categories the user has permission for
    """
    from news.models import Category
    
    if user.is_superuser:
        return Category.objects.all()
        
    # Get categories with specific permission
    permitted_categories = UserPermission.objects.filter(
        user=user,
        content_type='article',
        permission_type__in=[permission_type, 'full']
    ).values_list('category', flat=True)
    
    # Check if user has global permission (category=None)
    has_global_permission = UserPermission.objects.filter(
        user=user,
        content_type='article',
        permission_type__in=[permission_type, 'full'],
        category__isnull=True
    ).exists()
    
    if has_global_permission:
        return Category.objects.all()
    
    return Category.objects.filter(id__in=permitted_categories)

def get_users_with_dashboard_access():
    """
    Get all users who have any dashboard permissions
    """
    user_ids = UserPermission.objects.values_list('user', flat=True).distinct()
    return User.objects.filter(id__in=user_ids) | User.objects.filter(is_superuser=True)

def setup_default_permissions(user):
    """
    Set up default permissions for a new user
    """
    # View permission for articles (read-only access)
    UserPermission.objects.create(
        user=user,
        content_type='article',
        permission_type='view',
        category=None  # All categories
    )
    
    # Other default permissions can be added here
    return True
