# Generated by Django 4.2.7 on 2023-12-10 12:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0003_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
    ]