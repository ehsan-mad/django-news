#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_portal.settings')
django.setup()

from news.models import Article, Category

def list_slugs():
    print("Articles:")
    for article in Article.objects.all():
        print(f"  {article.slug} - {article.title}")
    
    print("\nCategories:")
    for category in Category.objects.all():
        print(f"  {category.slug} - {category.name}")

if __name__ == "__main__":
    list_slugs()
