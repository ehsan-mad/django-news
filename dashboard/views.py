from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden

from news.models import Article, Category
from .models import UserPermission, DashboardSettings, ActivityLog
from .permissions import (
    user_has_permission, 
    get_user_permitted_categories,
    get_users_with_dashboard_access,
    setup_default_permissions
)

import json
from datetime import timedelta, datetime

# Dashboard Home/Index
@login_required
def dashboard_index(request):
    """Dashboard home page with stats and recent activity"""
    # Get dashboard settings
    settings = DashboardSettings.get_settings()
    
    # Articles statistics
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(status='published').count()
    draft_articles = Article.objects.filter(status='draft').count()
    
    # Get recent articles
    recent_articles = Article.objects.select_related('author', 'category').order_by('-created_at')[:5]
    
    # Get trending articles if enabled
    trending_articles = None
    if settings.show_trending_articles:
        week_ago = timezone.now() - timedelta(days=7)
        trending_articles = Article.objects.filter(
            status='published',
            published_at__gte=week_ago
        ).select_related('category', 'author').order_by('-views_count')[:5]
    
    # User statistics
    total_users = User.objects.count()
    
    # Recent activity
    recent_activity = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Basic analytics
    today = timezone.now().date()
    articles_today = Article.objects.filter(created_at__date=today).count()
    
    # Last 7 days article stats for chart
    days = []
    article_counts = []
    
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        day_start = datetime.combine(day.date(), datetime.min.time())
        day_end = datetime.combine(day.date(), datetime.max.time())
        
        count = Article.objects.filter(created_at__range=(day_start, day_end)).count()
        days.append(day.date().strftime('%a'))
        article_counts.append(count)
    
    # Category stats
    categories = Category.objects.annotate(article_count=Count('articles')).order_by('-article_count')[:5]
    
    context = {
        'title': 'Dashboard',
        'settings': settings,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'recent_articles': recent_articles,
        'trending_articles': trending_articles,
        'total_users': total_users,
        'recent_activity': recent_activity,
        'articles_today': articles_today,
        'days': json.dumps(days),
        'article_counts': json.dumps(article_counts),
        'categories': categories,
    }
    
    return render(request, 'dashboard/index.html', context)

# User Management Views
@login_required
def user_list(request):
    """List all users with dashboard access"""
    if not user_has_permission(request.user, 'user', 'view'):
        messages.error(request, "You don't have permission to view users.")
        return redirect('dashboard:index')
    
    users = get_users_with_dashboard_access()
    
    context = {
        'title': 'Users',
        'users': users,
        'can_create': user_has_permission(request.user, 'user', 'create'),
        'can_edit': user_has_permission(request.user, 'user', 'edit'),
        'can_delete': user_has_permission(request.user, 'user', 'delete'),
    }
    
    return render(request, 'dashboard/users/list.html', context)

@login_required
def user_create(request):
    """Create a new user with dashboard access"""
    if not user_has_permission(request.user, 'user', 'create'):
        messages.error(request, "You don't have permission to create users.")
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_staff = request.POST.get('is_staff') == 'on'
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff
            )
            
            # Set up default permissions
            setup_default_permissions(user)
            
            # Process permissions from form
            for key, value in request.POST.items():
                if key.startswith('perm_'):
                    _, content_type, permission_type = key.split('_')
                    if value == 'on':
                        UserPermission.objects.create(
                            user=user,
                            content_type=content_type,
                            permission_type=permission_type
                        )
            
            messages.success(request, f"User '{username}' created successfully!")
            return redirect('dashboard:user_list')
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
    
    # Get all categories for permission assignment
    categories = Category.objects.all()
    
    context = {
        'title': 'Create User',
        'categories': categories,
    }
    
    return render(request, 'dashboard/users/create.html', context)

@login_required
def user_edit(request, user_id):
    """Edit an existing user"""
    if not user_has_permission(request.user, 'user', 'edit'):
        messages.error(request, "You don't have permission to edit users.")
        return redirect('dashboard:user_list')
    
    user_obj = get_object_or_404(User, id=user_id)
    
    # Don't allow editing superusers unless you're a superuser
    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit superusers.")
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        # Update user fields
        user_obj.username = request.POST.get('username')
        user_obj.email = request.POST.get('email')
        user_obj.first_name = request.POST.get('first_name')
        user_obj.last_name = request.POST.get('last_name')
        user_obj.is_staff = request.POST.get('is_staff') == 'on'
        
        # Only set password if provided
        password = request.POST.get('password')
        if password:
            user_obj.set_password(password)
            
        user_obj.save()
        
        # Update permissions - first remove all existing
        UserPermission.objects.filter(user=user_obj).delete()
        
        # Then add new permissions from form
        for key, value in request.POST.items():
            if key.startswith('perm_'):
                _, content_type, permission_type = key.split('_')
                if value == 'on':
                    # Check if category specific
                    category_id = request.POST.get(f'cat_{content_type}_{permission_type}')
                    category = None
                    if category_id and category_id != 'all':
                        category = Category.objects.get(id=category_id)
                    
                    UserPermission.objects.create(
                        user=user_obj,
                        content_type=content_type,
                        permission_type=permission_type,
                        category=category
                    )
        
        messages.success(request, f"User '{user_obj.username}' updated successfully!")
        return redirect('dashboard:user_list')
    
    # Get user's current permissions
    permissions = UserPermission.objects.filter(user=user_obj)
    
    # Get all categories for permission assignment
    categories = Category.objects.all()
    
    context = {
        'title': f'Edit User: {user_obj.username}',
        'user_obj': user_obj,
        'permissions': permissions,
        'categories': categories,
    }
    
    return render(request, 'dashboard/users/edit.html', context)

@login_required
def user_delete(request, user_id):
    """Delete a user"""
    if not user_has_permission(request.user, 'user', 'delete'):
        messages.error(request, "You don't have permission to delete users.")
        return redirect('dashboard:user_list')
    
    user_obj = get_object_or_404(User, id=user_id)
    
    # Don't allow deleting superusers unless you're a superuser
    if user_obj.is_superuser and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete superusers.")
        return redirect('dashboard:user_list')
    
    # Don't allow self-deletion
    if user_obj == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        messages.success(request, f"User '{username}' deleted successfully!")
        return redirect('dashboard:user_list')
    
    context = {
        'title': f'Delete User: {user_obj.username}',
        'user_obj': user_obj,
    }
    
    return render(request, 'dashboard/users/delete.html', context)

# Article Management Views
@login_required
def article_list(request):
    """List all articles with filtering options"""
    if not user_has_permission(request.user, 'article', 'view'):
        messages.error(request, "You don't have permission to view articles.")
        return redirect('dashboard:index')
    
    # Get filters from request
    status_filter = request.GET.get('status', 'all')
    category_filter = request.GET.get('category', 'all')
    search_query = request.GET.get('q', '')
    
    # Start with all articles
    articles = Article.objects.select_related('author', 'category')
    
    # Apply filters
    if status_filter != 'all':
        articles = articles.filter(status=status_filter)
    
    if category_filter != 'all':
        articles = articles.filter(category_id=category_filter)
    
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # If not superuser, limit to permitted categories
    if not request.user.is_superuser:
        permitted_categories = get_user_permitted_categories(request.user, 'view')
        articles = articles.filter(category__in=permitted_categories)
    
    # Order by most recent first
    articles = articles.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(articles, DashboardSettings.get_settings().articles_per_page)
    page = request.GET.get('page', 1)
    articles_page = paginator.get_page(page)
    
    # Get all categories for filter dropdown
    categories = Category.objects.all()
    
    context = {
        'title': 'Articles',
        'articles': articles_page,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'can_create': user_has_permission(request.user, 'article', 'create'),
        'can_edit': user_has_permission(request.user, 'article', 'edit'),
        'can_delete': user_has_permission(request.user, 'article', 'delete'),
        'can_publish': user_has_permission(request.user, 'article', 'publish'),
    }
    
    return render(request, 'dashboard/articles/list.html', context)

@login_required
def article_create(request):
    """Create a new article"""
    if not user_has_permission(request.user, 'article', 'create'):
        messages.error(request, "You don't have permission to create articles.")
        return redirect('dashboard:article_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category')
        status = request.POST.get('status')
        is_featured = request.POST.get('is_featured') == 'on'
        is_breaking_news = request.POST.get('is_breaking_news') == 'on'
        breaking_news_text = request.POST.get('breaking_news_text', '')
        
        try:
            category = Category.objects.get(id=category_id)
            
            # Check if user has permission for this category
            if not request.user.is_superuser:
                if not user_has_permission(request.user, 'article', 'create', category):
                    messages.error(request, f"You don't have permission to create articles in {category.name} category.")
                    return redirect('dashboard:article_list')
            
            # Create article
            article = Article(
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                author=request.user,
                status=status,
                is_featured=is_featured,
                is_breaking_news=is_breaking_news,
                breaking_news_text=breaking_news_text
            )
            
            # Handle featured image if uploaded
            if 'featured_image' in request.FILES:
                article.featured_image = request.FILES['featured_image']
            
            # Handle featured image URL if provided
            featured_image_url = request.POST.get('featured_image_url')
            if featured_image_url:
                article.featured_image_url = featured_image_url
                
            article.save()
            
            messages.success(request, f"Article '{title}' created successfully!")
            return redirect('dashboard:article_list')
        except Exception as e:
            messages.error(request, f"Error creating article: {str(e)}")
    
    # Get permitted categories
    if request.user.is_superuser:
        categories = Category.objects.all()
    else:
        categories = get_user_permitted_categories(request.user, 'create')
    
    context = {
        'title': 'Create Article',
        'categories': categories,
    }
    
    return render(request, 'dashboard/articles/create.html', context)

@login_required
def article_edit(request, article_id):
    """Edit an existing article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Check if user has permission to edit this article
    if not user_has_permission(request.user, 'article', 'edit', article.category):
        messages.error(request, "You don't have permission to edit this article.")
        return redirect('dashboard:article_list')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        excerpt = request.POST.get('excerpt')
        category_id = request.POST.get('category')
        status = request.POST.get('status')
        is_featured = request.POST.get('is_featured') == 'on'
        is_breaking_news = request.POST.get('is_breaking_news') == 'on'
        breaking_news_text = request.POST.get('breaking_news_text', '')
        
        try:
            category = Category.objects.get(id=category_id)
            
            # Check if user has permission for the new category
            if not request.user.is_superuser:
                if not user_has_permission(request.user, 'article', 'edit', category):
                    messages.error(request, f"You don't have permission to edit articles in {category.name} category.")
                    return redirect('dashboard:article_list')
            
            # Update article
            article.title = title
            article.content = content
            article.excerpt = excerpt
            article.category = category
            article.status = status
            article.is_featured = is_featured
            article.is_breaking_news = is_breaking_news
            article.breaking_news_text = breaking_news_text
            
            # Handle featured image if uploaded
            if 'featured_image' in request.FILES:
                article.featured_image = request.FILES['featured_image']
            elif request.POST.get('remove_image') == 'on':
                article.featured_image = None
                
            # Handle featured image URL if provided
            featured_image_url = request.POST.get('featured_image_url')
            if featured_image_url:
                article.featured_image_url = featured_image_url
            elif request.POST.get('remove_image_url') == 'on':
                article.featured_image_url = None
                
            article.save()
            
            messages.success(request, f"Article '{title}' updated successfully!")
            return redirect('dashboard:article_list')
        except Exception as e:
            messages.error(request, f"Error updating article: {str(e)}")
    
    # Get permitted categories
    if request.user.is_superuser:
        categories = Category.objects.all()
    else:
        categories = get_user_permitted_categories(request.user, 'edit')
    
    context = {
        'title': f'Edit Article: {article.title}',
        'article': article,
        'categories': categories,
    }
    
    return render(request, 'dashboard/articles/edit.html', context)

@login_required
def article_delete(request, article_id):
    """Delete an article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Check if user has permission to delete this article
    if not user_has_permission(request.user, 'article', 'delete', article.category):
        messages.error(request, "You don't have permission to delete this article.")
        return redirect('dashboard:article_list')
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f"Article '{title}' deleted successfully!")
        return redirect('dashboard:article_list')
    
    context = {
        'title': f'Delete Article: {article.title}',
        'article': article,
    }
    
    return render(request, 'dashboard/articles/delete.html', context)

@login_required
def article_publish(request, article_id):
    """Publish an article"""
    article = get_object_or_404(Article, id=article_id)
    
    # Check if user has permission to publish this article
    if not user_has_permission(request.user, 'article', 'publish', article.category):
        messages.error(request, "You don't have permission to publish articles.")
        return redirect('dashboard:article_list')
    
    if request.method == 'POST':
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        
        messages.success(request, f"Article '{article.title}' published successfully!")
        return redirect('dashboard:article_list')
    
    context = {
        'title': f'Publish Article: {article.title}',
        'article': article,
    }
    
    return render(request, 'dashboard/articles/publish.html', context)

# Category Management Views
@login_required
def category_list(request):
    """List all categories"""
    if not user_has_permission(request.user, 'category', 'view'):
        messages.error(request, "You don't have permission to view categories.")
        return redirect('dashboard:index')
    
    categories = Category.objects.annotate(article_count=Count('articles'))
    
    context = {
        'title': 'Categories',
        'categories': categories,
        'can_create': user_has_permission(request.user, 'category', 'create'),
        'can_edit': user_has_permission(request.user, 'category', 'edit'),
        'can_delete': user_has_permission(request.user, 'category', 'delete'),
    }
    
    return render(request, 'dashboard/categories/list.html', context)

@login_required
def category_create(request):
    """Create a new category"""
    if not user_has_permission(request.user, 'category', 'create'):
        messages.error(request, "You don't have permission to create categories.")
        return redirect('dashboard:category_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        
        try:
            category = Category(
                name=name,
                description=description
            )
            
            # Only set slug if provided
            if slug:
                category.slug = slug
                
            category.save()
            
            messages.success(request, f"Category '{name}' created successfully!")
            return redirect('dashboard:category_list')
        except Exception as e:
            messages.error(request, f"Error creating category: {str(e)}")
    
    context = {
        'title': 'Create Category',
    }
    
    return render(request, 'dashboard/categories/create.html', context)

@login_required
def category_edit(request, category_id):
    """Edit an existing category"""
    if not user_has_permission(request.user, 'category', 'edit'):
        messages.error(request, "You don't have permission to edit categories.")
        return redirect('dashboard:category_list')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        
        try:
            category.name = name
            category.description = description
            
            # Only update slug if provided
            if slug:
                category.slug = slug
                
            category.save()
            
            messages.success(request, f"Category '{name}' updated successfully!")
            return redirect('dashboard:category_list')
        except Exception as e:
            messages.error(request, f"Error updating category: {str(e)}")
    
    context = {
        'title': f'Edit Category: {category.name}',
        'category': category,
    }
    
    return render(request, 'dashboard/categories/edit.html', context)

@login_required
def category_delete(request, category_id):
    """Delete a category"""
    if not user_has_permission(request.user, 'category', 'delete'):
        messages.error(request, "You don't have permission to delete categories.")
        return redirect('dashboard:category_list')
    
    category = get_object_or_404(Category, id=category_id)
    
    # Check if category has articles
    article_count = category.articles.count()
    
    if request.method == 'POST':
        # Get confirmation and handling method
        confirm = request.POST.get('confirm')
        handling = request.POST.get('handling')
        
        if confirm == 'yes':
            try:
                if article_count > 0:
                    if handling == 'delete':
                        # Delete all articles in this category
                        category.articles.all().delete()
                    elif handling == 'move':
                        # Move articles to another category
                        new_category_id = request.POST.get('new_category')
                        new_category = get_object_or_404(Category, id=new_category_id)
                        
                        for article in category.articles.all():
                            article.category = new_category
                            article.save()
                
                name = category.name
                category.delete()
                messages.success(request, f"Category '{name}' deleted successfully!")
                return redirect('dashboard:category_list')
            except Exception as e:
                messages.error(request, f"Error deleting category: {str(e)}")
    
    # Get other categories for move option
    other_categories = Category.objects.exclude(id=category_id)
    
    context = {
        'title': f'Delete Category: {category.name}',
        'category': category,
        'article_count': article_count,
        'other_categories': other_categories,
    }
    
    return render(request, 'dashboard/categories/delete.html', context)

# Dashboard Settings View
@login_required
def settings(request):
    """Manage dashboard settings"""
    # Only superusers can change settings
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to change dashboard settings.")
        return redirect('dashboard:index')
    
    settings = DashboardSettings.get_settings()
    
    if request.method == 'POST':
        try:
            settings.site_name = request.POST.get('site_name')
            settings.primary_color = request.POST.get('primary_color')
            settings.enable_analytics = request.POST.get('enable_analytics') == 'on'
            settings.show_trending_articles = request.POST.get('show_trending_articles') == 'on'
            settings.articles_per_page = int(request.POST.get('articles_per_page'))
            
            # Handle logo upload
            if 'logo' in request.FILES:
                settings.logo = request.FILES['logo']
                
            settings.save()
            
            messages.success(request, "Dashboard settings updated successfully!")
            return redirect('dashboard:settings')
        except Exception as e:
            messages.error(request, f"Error updating settings: {str(e)}")
    
    context = {
        'title': 'Dashboard Settings',
        'settings': settings,
    }
    
    return render(request, 'dashboard/settings.html', context)

# Authentication Views
def login_view(request):
    """Login to dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has any dashboard permissions or is superuser
            has_permissions = user.is_superuser or UserPermission.objects.filter(user=user).exists()
            
            if has_permissions:
                login(request, user)
                
                # Log login activity
                ActivityLog.objects.create(
                    user=user,
                    action='login',
                    content_type='dashboard',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                return redirect('dashboard:index')
            else:
                messages.error(request, "You don't have permission to access the dashboard.")
        else:
            messages.error(request, "Invalid username or password.")
    
    # Get dashboard settings for branding
    settings = DashboardSettings.get_settings()
    
    context = {
        'title': 'Login',
        'settings': settings,
    }
    
    return render(request, 'dashboard/login.html', context)

@login_required
def logout_view(request):
    """Logout from dashboard"""
    # Log logout activity
    ActivityLog.objects.create(
        user=request.user,
        action='logout',
        content_type='dashboard',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('dashboard:login')

# Analytics
@login_required
def analytics(request):
    """View analytics data"""
    if not DashboardSettings.get_settings().enable_analytics:
        messages.warning(request, "Analytics are currently disabled.")
        return redirect('dashboard:index')
    
    # Time period filter
    period = request.GET.get('period', 'week')
    
    if period == 'day':
        start_date = timezone.now() - timedelta(days=1)
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
    else:  # week (default)
        start_date = timezone.now() - timedelta(days=7)
    
    # Article statistics
    total_views = Article.objects.filter(
        status='published'
    ).aggregate(total_views=Sum('views_count'))['total_views'] or 0
    
    # Popular articles
    popular_articles = Article.objects.filter(
        status='published',
        published_at__gte=start_date
    ).order_by('-views_count')[:10]
    
    # Category distribution
    categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published')),
        view_count=Sum('articles__views_count', filter=Q(articles__status='published'))
    ).order_by('-view_count')
    
    # Monthly article creation
    months_data = []
    month_labels = []
    
    for i in range(5, -1, -1):
        month_start = timezone.now().replace(day=1) - timedelta(days=i*30)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        month_count = Article.objects.filter(
            created_at__range=(month_start, month_end)
        ).count()
        
        months_data.append(month_count)
        month_labels.append(month_start.strftime('%b %Y'))
    
    context = {
        'title': 'Analytics',
        'total_views': total_views,
        'popular_articles': popular_articles,
        'categories': categories,
        'period': period,
        'months_data': json.dumps(months_data),
        'month_labels': json.dumps(month_labels),
    }
    
    return render(request, 'dashboard/analytics.html', context)
