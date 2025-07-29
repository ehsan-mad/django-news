# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_add_breaking_news_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='content',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='article',
            name='excerpt',
            field=models.TextField(blank=True, help_text='Brief description of the article', max_length=500),
        ),
        migrations.AddField(
            model_name='article',
            name='published_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='featured_image_url',
            field=models.URLField(blank=True, help_text='Alternative to uploaded image. URL to an external image.', max_length=500, null=True),
        ),
        migrations.RenameField(
            model_name='article',
            old_name='update_date',
            new_name='updated_at',
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey(null=True, on_delete=models.deletion.CASCADE, related_name='articles', to='news.category'),
        ),
    ]
