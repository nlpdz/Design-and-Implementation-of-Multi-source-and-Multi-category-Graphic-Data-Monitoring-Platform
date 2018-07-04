# Generated by Django 2.0.2 on 2018-03-26 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataDisplay', '0003_headline_images_headline_title_and_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='wangyi_news',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.TextField(max_length=100, null=True)),
                ('tag', models.TextField(max_length=100, null=True)),
                ('overview', models.TextField(max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='wangyi_news_images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fk_id', models.IntegerField(null=True)),
                ('imgurl', models.CharField(max_length=100, null=True)),
                ('note', models.TextField(max_length=1000, null=True)),
            ],
        ),
    ]