from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin
from .models import UserActivity, ActivityType

class UserActivityMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log user activity
    """
    EXCLUDED_PATHS = [
        '/static/', 
        '/media/',
        '/favicon.ico',
        '/admin/jsi18n/',
    ]
    
    def should_log(self, request):
        """Check if the request should be logged"""
        # Don't log excluded paths
        path = request.path_info
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            return False
            
        # Don't log OPTIONS or HEAD requests
        if request.method in ('OPTIONS', 'HEAD'):
            return False
            
        return True
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """Log the view being accessed"""
        if not self.should_log(request) or not request.user.is_authenticated:
            return None
            
        # Get view name and module
        view_name = view_func.__name__ if hasattr(view_func, '__name__') else str(view_func)
        module = view_func.__module__ if hasattr(view_func, '__module__') else ""
        
        # Determine if this is a data modification request
        activity_type = ActivityType.DATA_ACCESS
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            activity_type = ActivityType.DATA_MODIFICATION
            
        # Log the activity
        UserActivity.log(
            request=request,
            activity_type=activity_type,
            description=f"Accessed {view_name}",
            module=module.split('.')[0] if '.' in module else module,
            extra_data={
                'method': request.method,
                'path': request.path,
                'view': view_name,
            }
        )
        
        return None
