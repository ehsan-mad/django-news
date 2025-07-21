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
    cursor.execute("DESCRIBE news_article")
    
    print("Current database table structure for 'news_article':")
    print("Field\t\tType\t\t\tNull\tKey\tDefault\tExtra")
    print("-" * 80)
    
    for row in cursor.fetchall():
        print(f"{row[0]:<15}\t{row[1]:<20}\t{row[2]}\t{row[3]}\t{row[4]}\t{row[5]}")

if __name__ == "__main__":
    check_table_structure()
