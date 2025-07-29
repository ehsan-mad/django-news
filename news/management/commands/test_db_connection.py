# Path: news/management/commands/test_db_connection.py
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings

class Command(BaseCommand):
    help = 'Test database connection'

    def handle(self, *args, **options):
        try:
            # Test the connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                result = cursor.fetchone()
                
            self.stdout.write(
                self.style.SUCCESS(f"✅ Database connection successful!")
            )
            self.stdout.write(f"Database: {settings.DATABASES['default']['NAME']}")
            self.stdout.write(f"Host: {settings.DATABASES['default']['HOST']}")
            self.stdout.write(f"Engine: {settings.DATABASES['default']['ENGINE']}")
            self.stdout.write(f"PostgreSQL Version: {result[0]}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Database connection failed: {str(e)}")
            )
            self.stdout.write("Please check your .env file and Neon DB credentials.")
