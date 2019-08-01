# Generated by Django 2.1.1 on 2018-11-07 11:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('published', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, upload_to='images')),
                ('complete', models.BooleanField(default=False)),
                ('assigned_users', models.ManyToManyField(blank=True, related_name='assigned_posts', to=settings.AUTH_USER_MODEL)),
                ('authors', models.ManyToManyField(blank=True, related_name='authored_posts', to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(blank=True, related_name='posts', to='cms.Category')),
                ('saved_by_users', models.ManyToManyField(blank=True, related_name='saved_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'permissions': (('publish_post', 'Publish post'), ('assign_editors', 'Assign editors')),
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_reviews', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='cms.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authors', models.ManyToManyField(blank=True, related_name='subscriber_objects', to=settings.AUTH_USER_MODEL)),
                ('categories', models.ManyToManyField(blank=True, related_name='subscriptions', to='cms.Category')),
                ('owner', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
