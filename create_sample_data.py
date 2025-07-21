#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_portal.settings')
django.setup()

from news.models import Category, Article
from django.contrib.auth.models import User

def create_sample_data():
    # Create superuser if it doesn't exist
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created admin user: admin/admin123")
    else:
        admin_user = User.objects.get(username='admin')
        print("Using existing admin user")
    
    # Create categories
    categories_data = [
        {'name': 'Technology', 'description': 'Latest technology news and trends'},
        {'name': 'Sports', 'description': 'Sports news and updates'},
        {'name': 'Politics', 'description': 'Political news and analysis'},
        {'name': 'Entertainment', 'description': 'Entertainment and celebrity news'},
        {'name': 'Business', 'description': 'Business and finance news'},
    ]
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created category: {category.name}")
    
    # Create sample articles
    articles_data = [
        {
            'title': 'AI Revolution in 2025: What to Expect',
            'content': '''
            <p>Artificial Intelligence continues to transform industries across the globe. In 2025, we're seeing unprecedented developments in machine learning, natural language processing, and computer vision.</p>
            <p>Major tech companies are investing billions in AI research, leading to breakthrough applications in healthcare, education, and automation. This revolution is not just changing how we work, but how we live.</p>
            <p>Experts predict that AI will become even more integrated into our daily lives, from smart home systems to personalized learning platforms.</p>
            ''',
            'excerpt': 'Exploring the latest developments in artificial intelligence and their impact on society.',
            'category': 'Technology',
            'is_featured': True,
            'status': 'published',
        },
        {
            'title': 'Championship Finals Draw Record Viewership',
            'content': '''
            <p>The championship finals broke all previous viewership records, with over 100 million viewers tuning in worldwide.</p>
            <p>The thrilling match between two legendary teams kept fans on the edge of their seats for the entire duration. Social media buzzed with excitement as key moments unfolded.</p>
            <p>This historic event will be remembered as one of the greatest sporting spectacles of our time.</p>
            ''',
            'excerpt': 'Historic championship finals captivates global audience with record-breaking viewership.',
            'category': 'Sports',
            'is_featured': True,
            'status': 'published',
        },
        {
            'title': 'New Economic Policies Announced',
            'content': '''
            <p>Government officials announced a comprehensive set of economic policies aimed at boosting growth and reducing unemployment.</p>
            <p>The new policies include tax incentives for small businesses, infrastructure investment programs, and education reform initiatives.</p>
            <p>Economic analysts are optimistic about the potential impact of these measures on the national economy.</p>
            ''',
            'excerpt': 'Government unveils ambitious economic reform package to stimulate growth.',
            'category': 'Politics',
            'status': 'published',
        },
        {
            'title': 'Blockbuster Movie Breaks Box Office Records',
            'content': '''
            <p>The latest blockbuster film has shattered box office records in its opening weekend, earning over $200 million globally.</p>
            <p>Critics and audiences alike have praised the movie's stunning visuals, compelling storyline, and outstanding performances.</p>
            <p>The film's success marks a significant milestone for the entertainment industry's post-pandemic recovery.</p>
            ''',
            'excerpt': 'New blockbuster film achieves unprecedented box office success worldwide.',
            'category': 'Entertainment',
            'status': 'published',
        },
        {
            'title': 'Tech Startup Secures Major Investment',
            'content': '''
            <p>A promising tech startup has secured $50 million in Series B funding from leading venture capital firms.</p>
            <p>The company, which specializes in sustainable energy solutions, plans to use the funding to expand operations and accelerate product development.</p>
            <p>This investment reflects growing investor confidence in clean technology and environmental sustainability.</p>
            ''',
            'excerpt': 'Sustainable energy startup raises significant funding for expansion plans.',
            'category': 'Business',
            'status': 'published',
        },
    ]
    
    for article_data in articles_data:
        category = Category.objects.get(name=article_data['category'])
        
        article, created = Article.objects.get_or_create(
            title=article_data['title'],
            defaults={
                'content': article_data['content'],
                'excerpt': article_data['excerpt'],
                'category': category,
                'author': admin_user,
                'is_featured': article_data.get('is_featured', False),
                'status': article_data['status'],
                'views_count': 0,
            }
        )
        if created:
            print(f"Created article: {article.title}")
    
    print(f"\nSample data created successfully!")
    print(f"Categories: {Category.objects.count()}")
    print(f"Articles: {Article.objects.count()}")
    print(f"Featured Articles: {Article.objects.filter(is_featured=True).count()}")

if __name__ == "__main__":
    create_sample_data()
