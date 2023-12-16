# Generated by Django 5.0 on 2023-12-16 04:41

from django.db import migrations, models

import api.models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0012_alter_lecturer_image_alter_user_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='image',
        ),
        migrations.AlterField(
            model_name='lecturer',
            name='image',
            field=models.ImageField(null=True, upload_to=api.models.upload_to, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='student',
            name='image',
            field=models.ImageField(null=True, upload_to=api.models.upload_to, verbose_name='Image'),
        ),
    ]