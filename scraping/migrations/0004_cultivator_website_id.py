# Generated by Django 4.0.6 on 2022-08-05 17:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0003_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='cultivator',
            name='website_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='scraping.website'),
            preserve_default=False,
        ),
    ]