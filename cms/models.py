from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(
        blank=False,
        unique=True,
        max_length=50,
    )

    def __str__(self):
        return self.name


class Post(models.Model):

    authors = models.ManyToManyField(
        User,
        related_name='authored_posts',
        blank=True,
    )
    title = models.CharField(
        blank=False,
        max_length=100,
    )
    content = models.TextField(
        blank=False,
    )
    published = models.BooleanField(
        default=False,
    )
    categories = models.ManyToManyField(
        Category,
        related_name='posts',
        blank=True
    )
    saved_by_users = models.ManyToManyField(
        User,
        related_name='saved_posts',
        blank=True,
    )
    assigned_users = models.ManyToManyField(
        User,
        related_name='assigned_posts',
        blank=True,
    )
    image = models.ImageField(
        blank=True,
        upload_to='images'
    )
    complete = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']
        permissions = (("publish_post", "Publish post"), ("assign_editors", "Assign editors"))


class Review(models.Model):

    content = models.TextField(
        blank=False,
    )
    editor = models.ForeignKey(
        User,
        related_name="post_reviews",
        blank=False,
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        related_name="reviews",
        on_delete=models.CASCADE,
    )


class Subscription(models.Model):
    owner = models.OneToOneField(
        User,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    authors = models.ManyToManyField(
        User,
        blank=True,
        related_name='subscriber_objects'
    )
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='subscriptions'
    )



