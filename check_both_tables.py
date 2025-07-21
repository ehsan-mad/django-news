#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.append(os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_portal.settings')
django.setup()

from django.db import connection

def check_table_structure():
    cursor = connection.cursor()
    
    print("=== Article Table Structure ===")
    cursor.execute("DESCRIBE news_article")
    for row in cursor.fetchall():
        print(f"{row[0]:<20} {row[1]:<25} {row[2]}")
    
    print("\n=== Category Table Structure ===")
    cursor.execute("DESCRIBE news_category")
    for row in cursor.fetchall():
        print(f"{row[0]:<20} {row[1]:<25} {row[2]}")

if __name__ == "__main__":
    check_table_structure()
