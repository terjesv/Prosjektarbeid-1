from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from website.forms import RegistrationForm


class LoginTest(TestCase):

    def test_login_form_view(self):

        response = self.client.post(reverse('login_form'),
                                    data={'username': "TestUser",
                                          'password': "123"}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)

        User.objects.create_user(username='TestUser', password='123')
        response = self.client.post(reverse('login_form'),
                                    data={'username': "TestUser",
                                          'password': "123"}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)


class RegistrationTest(TestCase):

    def test_registration_view_get(self):
        response = self.client.get(reverse('registration_form'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')
        self.failUnless(isinstance(response.context['form'], RegistrationForm))

    def test_registration_view_post(self):
        response = self.client.post(reverse('registration_form'),
                                    data={'username': 'TestUser',
                                          'password': '123'})
        self.assertRedirects(response, reverse('post_list'))
        self.assertEqual(User.objects.count(), 1)
        self.failUnless(User.objects.get(username='TestUser').is_active)