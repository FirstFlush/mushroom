# Generated by Django 4.0.6 on 2022-08-05 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0005_post_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='date',
            field=models.DateField(),
        ),
    ]
