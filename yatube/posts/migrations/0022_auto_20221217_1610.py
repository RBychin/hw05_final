# Generated by Django 2.2.16 on 2022-12-17 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20221217_1558'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='is_readed',
        ),
        migrations.RemoveField(
            model_name='follow',
            name='is_readed',
        ),
        migrations.RemoveField(
            model_name='like',
            name='is_readed',
        ),
        migrations.RemoveField(
            model_name='post',
            name='is_readed',
        ),
    ]
