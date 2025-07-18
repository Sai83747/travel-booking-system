# Generated by Django 5.1.7 on 2025-04-05 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0008_package_image_url'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='destination',
        ),
        migrations.AddField(
            model_name='review',
            name='content_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
