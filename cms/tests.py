from django.contrib.auth.models import Permission, User
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse

from django.contrib.auth.models import Group
from django.utils.http import urlencode

from cms.forms import ReviewForm
from cms.models import Post, Review


class PostTest(TestCase):
    def add_permission(self, codename, user=None):
        user = self.user if not user else user
        permission = Permission.objects.get(codename=codename)
        user.user_permissions.add(permission)

    def setUp(self):
        self.post = Post.objects.create(
            title='TITLE',
            content='CONTENT',
        )
        self.username = 'TEST_USER'
        self.password = 'TEST_PASS'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)

        Group.objects.create(name='editor')

    def test_str(self):
        self.assertEqual(str(self.post), self.post.title)

    def test_post_list_view(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view(self):
        response = self.client.get(reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.assertNotEqual(response.status_code, 200)

        self.post.published = True
        self.post.save()
        response = self.client.get(reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['review_form'], ReviewForm)

    def test_subscription_login_logout_view(self):
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 302)


    ##################### FUNCTION VIEWS ###################

    def test_publish_post_view(self):
        self.assertFalse(self.post.published)
        response = self.client.post('/{}/publish'.format(self.post.pk), {})
        self.assertEquals(response.status_code, 403)

        self.add_permission('publish_post')
        response = self.client.post('/{}/publish'.format(self.post.pk), {})
        self.assertEquals(response.status_code, 302)

        self.failUnless(Post.objects.get(pk=self.post.pk).published)

        response = self.client.post('/{}/publish'.format(self.post.pk), {})
        self.assertEquals(response.status_code, 302)
        self.failIf(Post.objects.get(pk=self.post.pk).published)

    def test_save_post_view(self):
        self.client.logout()
        response = self.client.post('/{}/save'.format(self.post.pk), {})
        self.assertEquals(response.status_code, 403)

        self.client.login(username=self.username, password=self.password)
        response = self.client.post('/{}/save'.format(self.post.pk), {})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.saved_posts.first(), self.post)

    def test_assign_post_view(self):
        response = self.client.post('/{}/assign'.format(self.post.pk), {})
        self.assertEquals(response.status_code, 403)
        self.add_permission('add_review')
        response = self.client.post('/{}/assign'.format(self.post.pk), {})
        self.assertEquals(response.status_code, 302)

    def test_review_form(self):
        form = ReviewForm(data={'content': "This is a review"})
        self.assertTrue(form.is_valid())

        form = ReviewForm(data={'content': ""})
        self.assertFalse(form.is_valid())

    def test_add_review_view(self):
        response = self.client.post('/{}/add_review'.format(self.post.pk), {'content': 'content'})
        self.assertEqual(response.status_code, 403)

        self.add_permission('add_review')
        response = self.client.post('/{}/add_review'.format(self.post.pk), {'content': 'content'})
        self.assertEqual(response.status_code, 302)

    def test_delete_review_view(self):
        review = Review.objects.create(
            editor=self.user,
            post=self.post,
            content='review',
        )
        response = self.client.post('/{}/delete_review'.format(review.pk), {})
        self.assertEqual(response.status_code, 302)
        user = User.objects.create(
            username='otheruser',
        )
        review = Review.objects.create(
            editor=user,
            post=self.post,
            content='review',
        )
        response = self.client.post('/{}/delete_review'.format(review.pk), {})
        self.assertEqual(response.status_code, 403)

    def test_assign_editors(self):
        editor = User.objects.create_user(username='editor', password='123')
        permission = Permission.objects.get(codename='add_review')
        editor.user_permissions.add(permission)
        response = self.client.post('/{}/assign_editor'.format(self.post.pk),
                                    data={'editors': [editor.pk]})
        self.assertEqual(response.status_code, 403)

        self.add_permission('assign_editors')

        response = self.client.post('/{}/assign_editor'.format(self.post.pk),
                                    data={'editors': [editor.pk]})
        self.assertEqual(response.status_code, 302)

    ######## PERMISSIONS ###########

    def test_add_post(self):
        response = self.client.get(reverse('post_form'))
        self.assertNotEqual(response.status_code, 200)

        self.add_permission('add_post')
        response = self.client.get(reverse('post_form'))
        self.assertEqual(response.status_code, 200)

    def test_post_update_view_author(self):
        response = self.client.get(reverse('post_update', kwargs={'pk': self.post.pk}))
        self.assertNotEqual(response.status_code, 200)

        self.post.authors.add(self.user)
        self.post.save()
        response = self.client.get(reverse('post_update', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_draft_list_view(self):
        response = self.client.get(reverse('draft_list'))
        self.assertNotEqual(response.status_code, 200)

        self.user.is_superuser = True
        self.user.save()
        self.add_permission('change_post')
        response = self.client.get(reverse('draft_list'))
        self.assertEqual(response.status_code, 200)

    def test_delete_view(self):
        response = self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)

        self.post.authors.add(self.user)
        self.post.save()
        response = self.client.get(reverse('delete_post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_add_category_view(self):
        response = self.client.get(reverse('create_category'))
        self.assertEqual(response.status_code, 403)

        self.add_permission('add_category')
        response = self.client.get(reverse('create_category'))
        self.assertEqual(response.status_code, 200)

    def test_add_category_post(self):
        response = self.client.post('/add_category', data={'name': 'NAME'})
        self.assertEqual(response.status_code, 403)

        self.add_permission('add_category')
        response = self.client.post('/add_category', data={'name': 'NAME'})
        self.assertEqual(response.status_code, 302)
