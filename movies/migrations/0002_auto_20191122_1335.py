# Generated by Django 2.2.7 on 2019-11-22 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genre',
            name='like_users',
        ),
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(default='testtest', max_length=100),
            preserve_default=False,
        ),
    ]
