# Generated by Django 2.0.2 on 2018-03-27 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataDisplay', '0008_baidu_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='headline_images',
            name='abstracts',
            field=models.TextField(max_length=100, null=True),
        ),
    ]