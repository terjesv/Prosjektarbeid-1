from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from .models import Post, Category
from django.contrib.auth.models import Group, User, Permission
import random

# Titles
title1 = "POST - TITLE"
title2 = "This Post is Published"
title3 = "Toilets! And Why You Should Use Them"
draft_title3 = "This Post is a Draft (Meaning Unpublished)"

title_lst = [title1, title2, title3]

#Content
content1 = "Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of \"de Finibus Bonorum et Malorum\" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, \"Lorem ipsum dolor sit amet..\", comes from a line in section 1.10.32."
content2 = "There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc."
content3 = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

content_lst = [content1, content2, content3]

#
number_of_rnd_posts = 25

# This function creates dummy data to populate our site for testing

def populate(request):
    # Removes all existing content from site
    Group.objects.all().delete()
    Post.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()

    # Create 5 new Category objects
    cat1 = Category.objects.create(name="Friluft")
    cat2 = Category.objects.create(name="Skole")
    cat3 = Category.objects.create(name="Krim")
    cat4 = Category.objects.create(name="Sport")
    cat5 = Category.objects.create(name="Biler")

    # Creates the author and editor groups
    author_group = Group.objects.create(name='authors')
    editor_group = Group.objects.create(name='editor')
    executive_editor_group = Group.objects.create(name='executive_editor')

    # Creates misc users
    author_user_1 = User.objects.create_user(username='author', password='123')
    editor_user_1 = User.objects.create_user(username='editor', password='123')
    author_user_2 = User.objects.create_user(username='author2', password='123')
    executive_editor_1 = User.objects.create_user(username='exec_editor', password='123')
    admin = User.objects.create_user(username='admin', password='123')

    # Give the users different permissions
    admin.is_staff = True
    admin.is_superuser = True
    author_user_1.is_staff = True
    editor_user_1.is_staff = True
    author_user_2.is_staff = True
    executive_editor_1.is_staff = True
    author_user_1.groups.add(author_group)
    editor_user_1.groups.add(editor_group)
    author_user_2.groups.add(author_group)
    executive_editor_1.groups.add(executive_editor_group)

    # Create post objects
    post1 = Post.objects.create(title=title1, content=content1, published=True)
    post2 = Post.objects.create(title=title2, content=content2, published=True)
    post3 = Post.objects.create(title=title3, content=content3, published=True)
    draft1 = Post.objects.create(title=draft_title3, content=content1, published=False)

    # Add authors to posts
    post1.authors.set([author_user_1, author_user_2])
    post2.authors.add(author_user_1)
    post3.authors.add(author_user_2)

    # Give posts categories
    post1.categories.add(cat1, cat3, cat5)
    post2.categories.add(cat2)
    post3.categories.add(cat4, cat5)

    # Sets the permissions of the author group
    author_group_permissions = Permission.objects.filter(
        Q(codename='add_post') |
        Q(codename='change_post')
    )

    # Sets the permissions of the editor group
    editor_group_permissions = Permission.objects.filter(
        Q(codename='add_review') |
        Q(codename='change_post')
    )

    # Sets the permissions of the editor group
    executive_editor_group_permissions = Permission.objects.filter(
        Q(codename='publish_post') |
        Q(codename='add_review') |
        Q(codename='assign_editors') |
        Q(codename='change_post') |
        Q(codename='add_category')

    )

    for permission in author_group_permissions:
        author_group.permissions.add(permission)

    for permission in editor_group_permissions:
        editor_group.permissions.add(permission)

    for permission in executive_editor_group_permissions:
        executive_editor_group.permissions.add(permission)

    for django_object in [post1, post2, post3, draft1, author_user_1, editor_user_1, admin, author_group, editor_group, executive_editor_group, executive_editor_1]:
        django_object.save()

    return HttpResponseRedirect(reverse_lazy('post_list'))

