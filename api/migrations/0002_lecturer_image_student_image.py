# Generated by Django 4.2.7 on 2023-12-05 16:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecturer',
            name='image',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='image',
            field=models.CharField(max_length=100, null=True),
        ),
    ]