from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from .models import Profile


class UserRegisterForm(UserCreationForm):
    """
    Adds email field to the inherited fields.
    A form that creates a user, with no privileges, from the given username, password and email

    Arguments:
        UserCreationForm {class} -- What is being inherited
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
