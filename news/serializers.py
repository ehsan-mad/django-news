"""
API Serializers for Django News Portal

This module contains serializers that convert model instances to JSON
and validate incoming data for the REST API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Article


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for User model representing article authors.
    
    This serializer provides basic author information without sensitive data.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        """Return full name or username if names are not available."""
        return obj.get_full_name() or obj.username


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    
    Provides full CRUD operations for categories with automatic slug generation.
    """
    article_count = serializers.SerializerMethodField(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='api:category-detail', lookup_field='slug')
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'created_at', 
            'article_count', 'url'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'article_count', 'url']
    
    def get_article_count(self, obj):
        """Return the number of published articles in this category."""
        return obj.articles.filter(status='published').count()


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for category lists (used in article serializers).
    """
    url = serializers.HyperlinkedIdentityField(view_name='api:category-detail', lookup_field='slug')
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'url']
        read_only_fields = ['id', 'name', 'slug', 'url']


class ArticleListSerializer(serializers.ModelSerializer):
    """
    Serializer for article lists (optimized for performance).
    
    This serializer is used for list views and includes only essential fields
    to improve API performance.
    """
    author = AuthorSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)
    url = serializers.HyperlinkedIdentityField(view_name='api:article-detail', lookup_field='slug')
    featured_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image_url',
            'category', 'author', 'status', 'published_at', 'created_at',
            'url'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'created_at', 'url',
            'featured_image_url'
        ]
    
    def get_featured_image_url(self, obj):
        """Return absolute URL for featured image if exists."""
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for article detail view.
    
    This serializer includes all article fields and is used for
    detailed article views, create, and update operations.
    """
    author = AuthorSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    featured_image_url = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt',
            'featured_image', 'featured_image_url', 'category', 'category_id',
            'author', 'status', 'created_at', 'updated_at', 'published_at',
            'related_articles'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'created_at', 'updated_at',
            'featured_image_url', 'related_articles'
        ]
    
    def get_featured_image_url(self, obj):
        """Return absolute URL for featured image if exists."""
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None
    
    def get_related_articles(self, obj):
        """Return related articles from the same category."""
        related = obj.get_related_articles(count=3)
        return ArticleListSerializer(
            related, many=True, context=self.context
        ).data
    
    def validate_category_id(self, value):
        """Validate that the category exists."""
        try:
            Category.objects.get(id=value)
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist.")
    
    def create(self, validated_data):
        """Create article with authenticated user as author."""
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        
        article = Article.objects.create(
            category=category,
            author=self.context['request'].user,
            **validated_data
        )
        return article
    
    def update(self, instance, validated_data):
        """Update article, handling category_id if provided."""
        category_id = validated_data.pop('category_id', None)
        if category_id:
            category = Category.objects.get(id=category_id)
            instance.category = category
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ArticleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new articles.
    
    This serializer is optimized for article creation with proper validation.
    """
    category_id = serializers.IntegerField()
    
    class Meta:
        model = Article
        fields = [
            'title', 'content', 'excerpt', 'featured_image',
            'category_id', 'status'
        ]
    
    def validate_category_id(self, value):
        """Validate that the category exists."""
        try:
            Category.objects.get(id=value)
            return value
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist.")
    
    def create(self, validated_data):
        """Create article with authenticated user as author."""
        category_id = validated_data.pop('category_id')
        category = Category.objects.get(id=category_id)
        
        article = Article.objects.create(
            category=category,
            author=self.context['request'].user,
            **validated_data
        )
        return article
