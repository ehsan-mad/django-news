from django.db import models
from django.contrib.auth.models import User
from news.models import Category, Article

class UserPermission(models.Model):
    """
    Model to define custom permissions for users
    beyond the standard Django permissions system
    """
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
        ('publish', 'Publish'),
        ('full', 'Full Access'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('article', 'Article'),
        ('category', 'Category'),
        ('user', 'User'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_permissions')
    permission_type = models.CharField(max_length=20, choices=PERMISSION_CHOICES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    # Optional category restriction - if null, permission applies to all categories
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'permission_type', 'content_type', 'category']
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
    
    def __str__(self):
        category_str = f" ({self.category})" if self.category else " (all categories)"
        return f"{self.user.username} - {self.get_permission_type_display()} {self.content_type}{category_str}"


class DashboardSettings(models.Model):
    """
    Model to store dashboard settings and customizations
    """
    site_name = models.CharField(max_length=100, default="News Portal Admin")
    logo = models.ImageField(upload_to='dashboard/', null=True, blank=True)
    primary_color = models.CharField(max_length=20, default="#4F46E5")  # Indigo color
    enable_analytics = models.BooleanField(default=True)
    show_trending_articles = models.BooleanField(default=True)
    articles_per_page = models.PositiveIntegerField(default=10)
    
    class Meta:
        verbose_name = 'Dashboard Setting'
        verbose_name_plural = 'Dashboard Settings'
    
    def __str__(self):
        return "Dashboard Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if DashboardSettings.objects.exists() and not self.pk:
            return
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create dashboard settings"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class ActivityLog(models.Model):
    """
    Model to track user activity in the dashboard
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('publish', 'Published'),
        ('login', 'Logged In'),
        ('logout', 'Logged Out'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=50)  # e.g., 'article', 'category', 'user'
    object_id = models.PositiveIntegerField(null=True, blank=True)  # ID of the affected object
    object_repr = models.CharField(max_length=200, null=True, blank=True)  # String representation
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.content_type} at {self.timestamp}"
