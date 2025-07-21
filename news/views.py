# news/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import Article, Category

def home_view(request):
    """Homepage with latest and trending news"""
    # Featured articles
    featured_articles = Article.objects.filter(
        status='published', 
        is_featured=True
    ).select_related('category', 'author').order_by('-published_at')[:3]
    
    # Latest articles
    latest_articles = Article.objects.filter(
        status='published'
    ).select_related('category', 'author').order_by('-published_at')[:6]
    
    # Trending articles (most viewed in last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    trending_articles = Article.objects.filter(
        status='published',
        published_at__gte=week_ago
    ).select_related('category', 'author').order_by('-views_count')[:4]
    
    # Categories with article counts
    categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    ).filter(article_count__gt=0)
    
    context = {
        'featured_articles': featured_articles,
        'latest_articles': latest_articles,
        'trending_articles': trending_articles,
        'categories': categories,
        'page_title': 'Latest News'
    }
    return render(request, 'news/HomePage.html', context)

def article_detail_view(request, slug):
    """Individual article view"""
    article = get_object_or_404(
        Article.objects.select_related('category', 'author'),
        slug=slug,
        status='published'
    )
    
    # Increment view count
    Article.objects.filter(id=article.id).update(views_count=article.views_count + 1)
    article.views_count += 1
    
    # Related articles from same category
    related_articles = Article.objects.filter(
        category=article.category,
        status='published'
    ).exclude(id=article.id).select_related('category', 'author')[:4]
    
    # Recent articles for sidebar
    recent_articles = Article.objects.filter(
        status='published'
    ).exclude(id=article.id).select_related('category', 'author')[:5]
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'recent_articles': recent_articles,
        'page_title': article.title
    }
    return render(request, 'news/article_detail.html', context)

def category_articles_view(request, slug):
    """Category-wise articles"""
    category = get_object_or_404(Category, slug=slug)
    
    # Get articles for this category
    articles_list = Article.objects.filter(
        category=category,
        status='published'
    ).select_related('category', 'author').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles_list, 12)
    page = request.GET.get('page')
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Other categories for sidebar
    other_categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    ).exclude(id=category.id).filter(article_count__gt=0)
    
    context = {
        'category': category,
        'articles': articles,
        'other_categories': other_categories,
        'page_title': f'{category.name} News'
    }
    return render(request, 'news/category_articles.html', context)

def trending_articles_view(request):
    """Trending articles page"""
    days = int(request.GET.get('days', 7))
    if days not in [1, 7, 30]:
        days = 7
    
    date_filter = timezone.now() - timedelta(days=days)
    
    # Get trending articles
    articles_list = Article.objects.filter(
        status='published',
        published_at__gte=date_filter
    ).select_related('category', 'author').order_by('-views_count')
    
    # Pagination
    paginator = Paginator(articles_list, 12)
    page = request.GET.get('page')
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Popular categories
    popular_categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(
            articles__status='published',
            articles__published_at__gte=date_filter
        ))
    ).filter(article_count__gt=0).order_by('-article_count')[:5]
    
    context = {
        'articles': articles,
        'days': days,
        'popular_categories': popular_categories,
        'page_title': f'Trending Articles - Last {days} Day{"s" if days > 1 else ""}'
    }
    return render(request, 'news/trending_articles.html', context)

def search_view(request):
    """Search articles"""
    query = request.GET.get('q', '')
    articles_list = []
    
    if query:
        articles_list = Article.objects.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query),
            status='published'
        ).select_related('category', 'author').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles_list, 12)
    page = request.GET.get('page')
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'articles': articles,
        'query': query,
        'total_results': articles_list.count() if query else 0,
        'page_title': f'Search Results for "{query}"' if query else 'Search'
    }
    return render(request, 'news/search_results.html', context)

def archive_view(request):
    """Archive view with date-based filtering"""
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    articles_list = Article.objects.filter(status='published')
    
    if year:
        articles_list = articles_list.filter(published_at__year=year)
        if month:
            articles_list = articles_list.filter(published_at__month=month)
    
    articles_list = articles_list.select_related('category', 'author').order_by('-published_at')
    
    # Pagination
    paginator = Paginator(articles_list, 15)
    page = request.GET.get('page')
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    # Archive dates for sidebar
    archive_dates = Article.objects.filter(
        status='published'
    ).dates('published_at', 'month', order='DESC')[:12]
    
    context = {
        'articles': articles,
        'archive_dates': archive_dates,
        'selected_year': year,
        'selected_month': month,
        'page_title': 'News Archive'
    }
    return render(request, 'news/archive.html', context)

# Context processor for global template variables
def global_context(request):
    """Global context for all templates"""
    categories = Category.objects.annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    ).filter(article_count__gt=0).order_by('name')
    
    recent_articles = Article.objects.filter(
        status='published'
    ).select_related('category', 'author').order_by('-published_at')[:5]
    
    return {
        'categories': categories,
        'recent_articles': recent_articles,
    }

