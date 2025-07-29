# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_alter_article_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='show_breaking_image',
            field=models.BooleanField(default=True, help_text='Show article image in breaking news banner'),
        ),
    ]
