# news/urls.py
from django.urls import path
from . import views, api_views

app_name = 'news'

urlpatterns = [
    # Web views
    # path('', views.HomeView.as_view(), name='home'),
    # path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    # path('category/<str:category>/', views.CategoryView.as_view(), name='category'),
    # path('search/', views.search_view, name='search'),
    
    # API endpoints
    # path('api/articles/', api_views.ArticleListCreateAPIView.as_view(), name='api_article_list'),
    # path('api/articles/<slug:slug>/', api_views.ArticleDetailAPIView.as_view(), name='api_article_detail'),
    # path('api/categories/', api_views.CategoryListAPIView.as_view(), name='api_category_list'),
    # path('api/trending/', api_views.trending_articles, name='api_trending'),
    # path('api/featured/', api_views.featured_articles, name='api_featured'),
    path('', views.home_view, name='home'),
    path('article/<slug:slug>/', views.article_detail_view, name='article_detail'),
    path('category/<slug:slug>/', views.category_articles_view, name='category_articles'),
    path('trending/', views.trending_articles_view, name='trending'),
    path('search/', views.search_view, name='search'),
    path('archive/', views.archive_view, name='archive'),
]