from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'is_featured', 'is_breaking_news', 'breaking_image_display', 'has_image_display', 'published_at']
    list_filter = ['status', 'category', 'is_featured', 'is_breaking_news', 'show_breaking_image', 'created_at', 'published_at', 'author']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'image_preview']
    date_hierarchy = 'published_at'
    list_per_page = 20
    list_editable = ['is_featured', 'is_breaking_news']
    
    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'slug', 'category', 'status')
        }),
        ('Content', {
            'fields': ('excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_url', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Breaking News Options', {
            'fields': ('is_breaking_news', 'breaking_news_text', 'show_breaking_image'),
            'description': 'Configure breaking news settings for this article',
            'classes': ('wide',)
        }),
        ('Promotion', {
            'fields': ('is_featured',),
            'description': 'Set promotion options for this article'
        }),
        ('Publishing', {
            'fields': ('author', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.get_image_url():
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px;" />',
                obj.get_image_url()
            )
        return "No image"
    image_preview.short_description = "Image Preview"
    
    def has_image_display(self, obj):
        return obj.has_image()
    has_image_display.short_description = "Has Image"
    has_image_display.boolean = True
    
    def breaking_image_display(self, obj):
        if obj.is_breaking_news:
            return obj.show_breaking_image
        return None
    breaking_image_display.short_description = "Breaking Image"
    breaking_image_display.boolean = True

    def save_model(self, request, obj, form, change):
        if not change:  # Only set author on creation
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'author')
        
    class Media:
        js = ('js/admin-article.js',)
        css = {
            'all': ('css/admin-custom.css',)
        }
