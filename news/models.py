from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:category_articles', kwargs={'slug': self.slug})


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(default="")
    description = models.TextField(blank=True, default="", help_text="Article description")
    summary = models.TextField(blank=True, default="", help_text="Article summary")
    excerpt = models.TextField(max_length=500, blank=True, help_text="Brief description of the article")
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    featured_image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Alternative to uploaded image. URL to an external image.")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles', null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_breaking_news = models.BooleanField(default=False, help_text="Mark this article as breaking news to display in the banner")
    breaking_news_text = models.CharField(max_length=250, blank=True, help_text="Short text to display in the breaking news banner")
    show_breaking_image = models.BooleanField(default=False, help_text="Enable this option to display the article's image in the breaking news banner. If unchecked, only the text will be shown.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    update_date = models.DateTimeField(auto_now=True)
    publication_date = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['-views_count']),
            models.Index(fields=['status', '-views_count']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at and publication_date when status changes to published
        if self.status == 'published' and not self.published_at:
            now = timezone.now()
            self.published_at = now
            self.publication_date = now
        
        # Generate excerpt from content if not provided
        if not self.excerpt and self.content:
            # Remove HTML tags and limit to 300 characters
            import re
            plain_content = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = plain_content[:300] + '...' if len(plain_content) > 300 else plain_content
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.status == 'published' and (self.published_at or self.publication_date)

    def get_related_articles(self, count=3):
        return Article.objects.filter(
            category=self.category,
            status='published'
        ).exclude(id=self.id).order_by('-publication_date', '-published_at')[:count]

    def increment_views(self):
        """Increment article views count safely"""
        from django.db.models import F
        Article.objects.filter(id=self.id).update(views_count=F('views_count') + 1)
        self.refresh_from_db(fields=['views_count'])
        
    def get_image_url(self):
        """Returns the image URL for the article, prioritizing uploaded image"""
        if self.featured_image and hasattr(self.featured_image, 'url'):
            return self.featured_image.url
        elif self.featured_image_url:
            return self.featured_image_url
        return None
        
    def has_image(self):
        """Returns True if the article has an image (uploaded or URL)"""
        return bool(self.featured_image) or bool(self.featured_image_url)
