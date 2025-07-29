from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_add_featured_image_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='is_breaking_news',
            field=models.BooleanField(default=False, help_text='Mark this article as breaking news to display in the banner'),
        ),
        migrations.AddField(
            model_name='article',
            name='breaking_news_text',
            field=models.CharField(blank=True, help_text='Short text to display in the breaking news banner', max_length=250),
        ),
    ]
