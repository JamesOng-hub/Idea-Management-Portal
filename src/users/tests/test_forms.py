from django.test import TestCase
from users.forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.models import User
from django.urls import reverse

class UserRegisterFormTest(TestCase):

    def test_user_register_form_email_label(self):
        form = UserRegisterForm()
        self.assertTrue(form.fields['email'].label == None or form.fields['email'].label == 'email')

    def test_user_register_form_valid(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@email.com',
            'password1': 'helloworld123',
            'password2': 'helloworld123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_user_register_form_sign_up(self):
        response = self.client.post(reverse('account_signup'), data={
            'username': 'testuser',
            'email': 'testuser@email.com',
            'password1': 'helloworld123',
            'password2': 'helloworld123'
        })

        self.assertRedirects(response, '/accounts/confirm-email/', status_code=302, 
        target_status_code=200, fetch_redirect_response=True)

        users = User.objects.all()
        self.assertEqual(users.count(), 1)
        

class UserUpdateFormTest(TestCase):

    def test_user_update_form_email_label(self):
        form = UserUpdateForm()
        self.assertTrue(form.fields['email'].label == None or form.fields['email'].label == 'email')

    def test_user_update_form_valid(self):
        form_data = {
            'username': 'testuser', 
            'email': 'testuser@email.com'
        }
        form = UserUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

class ProfileUpdateFormTest(TestCase):

    def test_profile_update_form_valid(self):
        form_data = {
            'bio': 'testuser', 
            'occupation': '',
            'location': '',
            'image': 'default.jpg'
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

