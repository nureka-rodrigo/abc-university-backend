# Generated by Django 5.0 on 2023-12-16 04:36

from django.db import migrations, models

import api.models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0009_remove_user_image_lecturer_image_student_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lecturer',
            name='image',
        ),
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(null=True, upload_to=api.models.upload_to, verbose_name='Image'),
        ),
        migrations.AlterField(
            model_name='student',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=api.models.upload_to, verbose_name='Image'),
        ),
    ]