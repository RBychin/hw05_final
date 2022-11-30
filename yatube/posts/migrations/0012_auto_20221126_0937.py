# Generated by Django 2.2.16 on 2022-11-26 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-pub_date']},
        ),
        migrations.RemoveField(
            model_name='comment',
            name='create',
        ),
        migrations.AddField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=None, verbose_name='Дата'),
            preserve_default=False,
        ),
    ]
