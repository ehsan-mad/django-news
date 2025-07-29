from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
from .models import UserPermission, ActivityLog


class DashboardPermissionMiddleware:
    """
    Middleware to check if a user has permission to access
    specific dashboard views based on their custom permissions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)
            
        # Skip middleware for these paths
        if any(path in request.path for path in [
            '/admin/', '/api/', '/media/', '/static/', 
            reverse('dashboard:login'), reverse('dashboard:logout')
        ]):
            return self.get_response(request)
            
        # Always allow superusers
        if request.user.is_superuser:
            return self.get_response(request)
            
        # Check if we're in the dashboard
        if '/dashboard/' in request.path and not request.path == reverse('dashboard:index'):
            # Get current view name
            resolved = resolve(request.path)
            view_name = resolved.view_name
            
            # Check permissions based on the view
            if 'article' in view_name:
                content_type = 'article'
            elif 'category' in view_name:
                content_type = 'category'  
            elif 'user' in view_name:
                content_type = 'user'
            else:
                # Default views like dashboard index are accessible to all logged in users
                return self.get_response(request)
                
            # Determine the required permission based on the view
            if 'delete' in view_name:
                required_permission = 'delete'
            elif 'edit' in view_name or 'update' in view_name:
                required_permission = 'edit'
            elif 'create' in view_name or 'add' in view_name:
                required_permission = 'create'
            elif 'publish' in view_name:
                required_permission = 'publish'
            else:
                required_permission = 'view'
                
            # Check if user has the required permission
            has_permission = UserPermission.objects.filter(
                user=request.user,
                content_type=content_type,
                permission_type__in=[required_permission, 'full']
            ).exists()
            
            if not has_permission:
                messages.error(
                    request, 
                    f"You don't have permission to {required_permission} {content_type}s."
                )
                return redirect('dashboard:index')
                
        # Log user activity
        if request.method == 'POST' and '/dashboard/' in request.path:
            self._log_activity(request)
            
        return self.get_response(request)
        
    def _log_activity(self, request):
        """Log user activities for POST requests"""
        action = None
        content_type = None
        object_id = None
        object_repr = None
        
        # Determine action and content type based on the URL pattern
        resolved = resolve(request.path)
        view_name = resolved.view_name
        
        if 'delete' in view_name:
            action = 'delete'
        elif 'edit' in view_name or 'update' in view_name:
            action = 'update'
        elif 'create' in view_name or 'add' in view_name:
            action = 'create'
        elif 'publish' in view_name:
            action = 'publish'
            
        if 'article' in view_name:
            content_type = 'article'
        elif 'category' in view_name:  
            content_type = 'category'
        elif 'user' in view_name:
            content_type = 'user'
            
        # Get object ID from URL kwargs or POST data
        if resolved.kwargs.get('pk'):
            object_id = resolved.kwargs.get('pk')
        elif request.POST.get('id'):
            object_id = request.POST.get('id')
            
        # Only log if we have enough information
        if action and content_type:
            ActivityLog.objects.create(
                user=request.user,
                action=action,
                content_type=content_type,
                object_id=object_id,
                object_repr=object_repr,
                ip_address=self._get_client_ip(request)
            )
            
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
