# Generated by Django 4.2.16 on 2025-07-28 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_add_missing_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='featured_image_url',
            field=models.URLField(blank=True, help_text='Alternative to uploaded image. URL to an external image.', max_length=500, null=True),
        ),
    ]
